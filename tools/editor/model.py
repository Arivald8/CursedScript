import json
import os
from collections import deque
from .cfg import CFG

class MapModel:
    def __init__(self, width=CFG.DEFAULT_WIDTH, height=CFG.DEFAULT_HEIGHT):
        self.width = width
        self.height = height
        self.map_data = []    # 2D array of chars
        self.entity_data = {} # Dict {(x, y): EntityDict}
        self.reset_map()

    def reset_map(self):
        """Creates a blank map."""
        self.map_data = [['.' for _ in range(self.width)] for _ in range(self.height)]
        self.entity_data = {}

    def resize(self, w, h):
        self.width = w
        self.height = h
        self.reset_map()

    # Data modification -->
    def set_terrain(self, x, y, char):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.map_data[y][x] = char
            return True
        return False
    
    def set_terrain(self, x, y, char):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.map_data[y][x] = char
            return True
        return False

    def get_terrain(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.map_data[y][x]
        return None

    def add_entity(self, x, y, entity_def):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.entity_data[(x, y)] = entity_def
            return True
        return False

    def remove_entity(self, x, y):
        if (x, y) in self.entity_data:
            del self.entity_data[(x, y)]
            return True
        return False
    # <-- Data modification
    
    # Algo -->
    def bucket_fill(self, start_x, start_y, fill_char):
        """
        Performs flood fill.
        Returns: List of (x, y) tuples that were changes.
        """
        target_char = self.get_terrain(start_x, start_y)
        if target_char == fill_char or target_char is None:
            return []

        changed_cells = []
        queue = deque([(start_x, start_y)])
        visited = set()

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited: 
                continue

            visited.add((cx, cy))

            if 0 <= cx < self.width and 0 <= cy < self.height:
                if self.map_data[cy][cx] == target_char:
                    self.map_data[cy][cx] = fill_char
                    changed_cells.append((cx, cy))
                    
                    queue.append((cx + 1, cy))
                    queue.append((cx - 1, cy))
                    queue.append((cx, cy + 1))
                    queue.append((cx, cy - 1))
        
        return changed_cells
    # <-- Algo

    # I/O -->
    def save_to_disk(self, filename):
        """
        Saves map and entities to a single JSON file.
        Uses the 'safe save' pattern (write temp --> flush --> rename)
        """
        # Data packet prep - flatted into a list for JSON storage
        entities_export = [
            {"x": k[0], "y": k[1], "id": v['id']} 
            for k, v in self.entity_data.items()
        ]

        full_data = {
            "meta": {"version": "1.0", "type": "cursed_map"},
            "dimensions": {"width": self.width, "height": self.height},
            "terrain": ["".join(row) for row in self.map_data],
            "entities": entities_export
        }

        # Atomic write
        temp_filename = filename + ".tmp"

        try:
            with open(temp_filename, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, indent=4)
                # Force OS to write buffer to disk
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic swap
            # This is atomic on POSIX. On Windows it's atomic in modern Python (os.replace)
            os.replace(temp_filename, filename)
            
        except Exception as e:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            raise IOError(f"Failed to save map: {str(e)}")

    def load_from_disk(self, filename):
        """
        Loads a unified JSON map file.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")

        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "dimensions" not in data or "terrain" not in data:
            raise ValueError("Invalid map file format")

        # Load dimenions
        self.width = data["dimensions"]["width"]
        self.height = data["dimensions"]["height"]
        
        # Load terrain
        raw_rows = data["terrain"]
        # Converting list of strings back to list of lists
        self.map_data = [list(row.ljust(self.width, '.')) for row in raw_rows]
        
        # Ensuring height matches data
        if len(self.map_data) < self.height:
            # Filling missing rows if file is corrupted/short
            for _ in range(self.height - len(self.map_data)):
                self.map_data.append(['.' * self.width])

        # Load entities
        self.entity_data = {}
        # Creating a lookup for entity definitions by ID
        entity_lookup = {e['id']: e for e in CFG.ENTITY_TYPES}

        for item in data.get("entities", []):
            eid = item.get("id")
            x, y = item.get("x"), item.get("y")
            
            if eid in entity_lookup:
                # Valid entity, place it
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.entity_data[(x, y)] = entity_lookup[eid]
    # <-- I/O