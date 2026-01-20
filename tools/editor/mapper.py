from tkinter import simpledialog
import tkinter as tk
from .cfg import CFG
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .editor import MapEditor
    from .handler import Handler

class Mapper:
    def __init__(
            self, 
            editor_instance: 'MapEditor', 
            handler_instance: 'Handler', 
            canvas_instance: tk.Canvas, 
        ):
        self.editor = editor_instance
        self.handler = handler_instance
        self.canvas = canvas_instance

    def prompt_new_map(self):
        # Using self.winfo_toplevel() to make sure dialogs center on the main app
        w = simpledialog.askinteger(
            "Size", 
            "Width:", 
            parent=self.editor.winfo_toplevel(), 
            initialvalue= CFG.DEFAULT_WIDTH, 
            minvalue=10
        )

        h = simpledialog.askinteger(
            "Size",
            "Height:",
            parent=self.editor.winfo_toplevel(),
            initialvalue=CFG.DEFAULT_HEIGHT, 
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
        
        self.canvas.config(scrollregion=(0, 0, self.editor.width * CFG.CELL_SIZE, self.editor.height * CFG.CELL_SIZE))
        
        lookup = {t['char']: t for t in CFG.TERRAIN_TYPES}

        for y in range(self.editor.height):
            row_ids = []
            for x in range(self.editor.width):
                char = self.editor.map_data[y][x]
                tile = lookup.get(char, CFG.TERRAIN_TYPES[0])
                
                x1, y1 = x * CFG.CELL_SIZE, y * CFG.CELL_SIZE
                x2, y2 = x1 + CFG.CELL_SIZE, y1 + CFG.CELL_SIZE
                
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=tile['color'], outline="")

                txt = self.canvas.create_text(
                    x1 + CFG.CELL_SIZE/2,
                    y1 + CFG.CELL_SIZE/2, 
                    text=tile['symbol'], 
                    fill=tile['fg'], 
                    font=("Arial", CFG.FONT_SIZE)
                )

                row_ids.append((rect, txt))
            self.editor.cell_ids.append(row_ids)
        
        # Redrawing entities if loading
        for coord, entity in self.editor.entity_data.items():
            self.editor.painter.draw_entity_visual(coord[0], coord[1], entity)