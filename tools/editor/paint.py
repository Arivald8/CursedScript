from collections import deque

class Paint:
    def __init__(self, editor_instance, cell_size):
        """
        :param editor_instance: Reference to the main MapEditor class
        :param cell_size: Int
        """
        self.editor = editor_instance
        self.cell_size = cell_size
        
    def paint_terrain(self, x, y):
        current_char = self.editor.current_terrain['char']

        # Check bounds safety check
        if 0 <= x < self.editor.width and 0 <= y < self.editor.height:
            if self.editor.map_data[y][x] != current_char:
                self.editor.map_data[y][x] = current_char
                self.update_cell_visual(x, y, self.editor.current_terrain)

    def bucket_fill(self, x, y, target_tile):
        target_char = self.editor.map_data[y][x]
        fill_char = target_tile['char']
        
        if target_char == fill_char: 
            return

        queue = deque([(x, y)])
        visited = set()
        
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited: 
                continue

            visited.add((cx, cy))
            
            if 0 <= cx < self.editor.width and 0 <= cy < self.editor.height:
                if self.editor.map_data[cy][cx] == target_char:
                    self.editor.map_data[cy][cx] = fill_char
                    self.update_cell_visual(cx, cy, target_tile)
                    
                    queue.append((cx+1, cy))
                    queue.append((cx-1, cy))
                    queue.append((cx, cy+1))
                    queue.append((cx, cy-1))

    def update_cell_visual(self, x, y, tile):
        rect, txt = self.editor.cell_ids[y][x]
        self.editor.canvas.itemconfig(rect, fill=tile['color'])
        self.editor.canvas.itemconfig(txt, text=tile['symbol'], fill=tile['fg'])

    def paint_entity(self, x, y):
        # Remove existing at this tile
        if (x, y) in self.editor.entity_data:
            self.erase_entity(x, y)
        
        self.editor.entity_data[(x, y)] = self.editor.current_entity
        self.draw_entity_visual(x, y, self.editor.current_entity)

    def draw_entity_visual(self, x, y, entity_def):
        cs = self.cell_size
        x1, y1 = x * cs + 2, y * cs + 2
        x2, y2 = x * cs + cs - 2, y * cs + cs - 2
        
        if entity_def['shape'] == 'star':
             # Simple circle for start to distinguish
             eid = self.editor.canvas.create_oval(
                x1, 
                y1, 
                x2, 
                y2, 
                fill=entity_def['color'], 
                outline="black", 
                width=2
            )
             
        elif entity_def['shape'] == 'diamond':
            # Diamond polygon
            cx, cy = x * cs + cs/2, y * cs + cs/2
            offset = cs/2 - 2
            eid = self.editor.canvas.create_polygon(
                cx, 
                cy-offset, 
                cx+offset, 
                cy, 
                cx, 
                cy+offset, 
                cx-offset, 
                cy, 
                fill=entity_def['color'], 
                outline="black"
            )

        else:
            eid = self.editor.canvas.create_oval(
                x1, 
                y1, 
                x2, 
                y2, 
                fill=entity_def['color'], 
                outline="black"
            )
            
        self.editor.entity_ids[(x, y)] = eid

    def erase_entity(self, x, y):
        if (x, y) in self.editor.entity_data:
            del self.editor.entity_data[(x, y)]
            if (x, y) in self.editor.entity_ids:
                self.editor.canvas.delete(self.editor.entity_ids[(x, y)])
                del self.editor.entity_ids[(x, y)]