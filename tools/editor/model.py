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
        # Save terrain
        with open(filename, 'w', encoding="utf-8") as f:
            for row in self.map_data:
                f.write("".join(row) + "\n")

        # Save entities
        json_filename = os.path.splitext(filename)[0] + "_data.json"
        export_list = [
            {"x": x, "y": y, "type": d['type'], "id": d['id']}
            for (x, y), d in self.entity_data.items()
        ]
        
        with open(json_filename, 'w', encoding="utf-8") as f:
            json.dump(export_list, f, indent=4)
        
        return json_filename

    def load_from_disk(self, filename):
        with open(filename, 'r', encoding="utf-8") as f:
            lines = [line.rstrip('\n') for line in f]
        
        self.height = len(lines)
        self.width = max(len(l) for l in lines) if lines else 0
        self.map_data = [list(line.ljust(self.width, '.')) for line in lines]
        
        # Load Entities
        self.entity_data = {}
        json_filename = os.path.splitext(filename)[0] + "_data.json"
        if os.path.exists(json_filename):
            with open(json_filename, 'r') as f:
                loaded = json.load(f)
            
            # Rehydrate entity data from ID
            # (In a real app, optimize this lookup)
            for item in loaded:
                for proto in CFG.ENTITY_TYPES:
                    if proto['id'] == item['id']:
                        self.entity_data[(item['x'], item['y'])] = proto
                        break
    # <-- I/O