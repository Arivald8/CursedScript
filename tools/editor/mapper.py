from tkinter import simpledialog, ttk

class Mapper:
    def __init__(self, editor_instance, handler_instance, canvas_instance, default_width, default_height, cell_size, terrain_types, font_size):
        self.editor = editor_instance
        self.handler = handler_instance
        self.canvas = canvas_instance
        self.default_width = default_width
        self.default_height = default_height
        self.cell_size = cell_size
        self.terrain_types = terrain_types
        self.font_size = font_size


    def prompt_new_map(self):
        # Using self.winfo_toplevel() to make sure dialogs center on the main app
        w = simpledialog.askinteger(
            "Size", 
            "Width:", 
            parent=self.editor.winfo_toplevel(), 
            initialvalue= self.default_width, 
            minvalue=10
        )

        h = simpledialog.askinteger(
            "Size",
            "Height:",
            parent=self.editor.winfo_toplevel(),
            initialvalue=self.default_height, 
            minvalue=10
        )

        if w and h:
            self.editor.width, self.editor.height = w, h
            self.new_map()

    def new_map(self):
        self.editor.map_data = [['.' for _ in range(self.editor.width)] for _ in range(self.editor.height)]
        self.editor.entity_data = {}
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        self.editor.cell_ids = []
        self.editor.entity_ids = {}
        
        self.canvas.config(scrollregion=(0, 0, self.editor.width * self.cell_size, self.editor.height * self.cell_size))
        
        lookup = {t['char']: t for t in self.terrain_types}

        for y in range(self.editor.height):
            row_ids = []
            for x in range(self.editor.width):
                char = self.editor.map_data[y][x]
                tile = lookup.get(char, self.terrain_types[0])
                
                x1, y1 = x * self.cell_size, y * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=tile['color'], outline="")

                txt = self.canvas.create_text(
                    x1 + self.cell_size/2,
                    y1 + self.cell_size/2, 
                    text=tile['symbol'], 
                    fill=tile['fg'], 
                    font=("Arial", self.font_size)
                )

                row_ids.append((rect, txt))
            self.editor.cell_ids.append(row_ids)
        
        # Redrawing entities if loading
        for coord, entity in self.editor.entity_data.items():
            self.editor.painter.draw_entity_visual(coord[0], coord[1], entity)