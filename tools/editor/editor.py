import tkinter as tk
from tkinter import simpledialog, ttk

from .paint import Paint
from .file_io import FileIO
from .handler import Handler

# CONF
DEFAULT_WIDTH = 60
DEFAULT_HEIGHT = 40
CELL_SIZE = 20  
FONT_SIZE = 10

TERRAIN_TYPES = [
    {'char': '.', 'color': '#32CD32', 'fg': '#006400', 'name': 'Grass',     'symbol': '·'},
    {'char': 'T', 'color': '#228B22', 'fg': '#000000', 'name': 'Tree',      'symbol': '♠'},
    {'char': '~', 'color': '#1E90FF', 'fg': '#E0FFFF', 'name': 'Water',     'symbol': '≈'},
    {'char': '#', 'color': '#DAA520', 'fg': '#8B4513', 'name': 'Road',      'symbol': '░'},
    {'char': ':', 'color': '#F0E68C', 'fg': '#BDB76B', 'name': 'Sand',      'symbol': '░'},
    {'char': '^', 'color': '#D3D3D3', 'fg': '#000000', 'name': 'Mountain',  'symbol': '▲'},
    {'char': 'x', 'color': '#696969', 'fg': '#D3D3D3', 'name': 'Wall',      'symbol': '▒'},
    {'char': 'M', 'color': '#2F4F4F', 'fg': '#708090', 'name': 'Cave/Rock', 'symbol': '█'},
    {'char': 'O', 'color': '#8B0000', 'fg': '#FFFFFF', 'name': 'Building',  'symbol': '⌂'},
    {'char': '+', 'color': '#4682B4', 'fg': '#FFD700', 'name': 'Bridge',    'symbol': '≡'},
    {'char': ' ', 'color': '#000000', 'fg': '#000000', 'name': 'Void',      'symbol': ''},
]

# (Saved to JSON)
ENTITY_TYPES = [
    {'type': 'player',   'id': 'player_start', 'name': 'Player Start', 'color': '#FFFFFF', 'shape': 'star'},
    {'type': 'creature', 'id': 'Ogre',         'name': 'Ogre',         'color': '#FF0000', 'shape': 'oval'},
    {'type': 'creature', 'id': 'Goblin',       'name': 'Goblin',       'color': '#FF69B4', 'shape': 'oval'},
    {'type': 'item',     'id': 'Sword',        'name': 'Sword',        'color': '#00FFFF', 'shape': 'diamond'},
    {'type': 'item',     'id': 'Potion',       'name': 'Health Pot',   'color': '#00FF00', 'shape': 'diamond'},
    {'type': 'item',     'id': 'Shield',       'name': 'Shield',       'color': '#FFA500', 'shape': 'diamond'},
]

class MapEditor(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        
        # Data State
        self.width = DEFAULT_WIDTH
        self.height = DEFAULT_HEIGHT
        self.map_data = []          # 2D array of chars
        self.entity_data = {}       # Dict: {(x,y): EntityDict}
        
        # Used in tool manager classes 
        self.toolbar = tk.Frame(self, width=250, bg="#e0e0e0", relief=tk.RAISED, bd=1)
        self.notebook = ttk.Notebook(self.toolbar)
        self.tool_var = tk.StringVar(value="brush")

        # Tools State
        self.painter = Paint(self, CELL_SIZE)
        self.file_io = FileIO(self, TERRAIN_TYPES, ENTITY_TYPES)
        self.handler = Handler(self, self.painter, self.notebook, self.tool_var, CELL_SIZE)

        self.selected_mode = "terrain" # 'terrain' or 'entity'
        self.current_terrain = TERRAIN_TYPES[0]
        self.current_entity = ENTITY_TYPES[0]
        self.tool_type = "brush"       # 'brush' or 'bucket'
        
        # Rendering State
        self.cell_ids = []          # Grid IDs (rect, text)
        self.entity_ids = {}        # Entity Canvas IDs {(x,y): id}

        self.setup_ui()
        self.new_map()

    def setup_ui(self):
        # Left: Toolbar
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)
        
        # File IO
        tk.Label(self.toolbar, text="   FILE   ", bg="#e0e0e0", font=("Arial", 9, "bold")).pack(pady=5)
        btn_frame = tk.Frame(self.toolbar, bg="#e0e0e0")
        btn_frame.pack(fill=tk.X, padx=5)

        tk.Button(btn_frame, text="New", command=self.prompt_new_map, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Save", command=self.file_io.save_map, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Load", command=self.file_io.load_map, width=8).pack(side=tk.LEFT, padx=2)

        tk.Label(self.toolbar, text="   TOOLS   ", bg="#e0e0e0", font=("Arial", 9, "bold")).pack(pady=(15, 5))
        
        # Tool select
        tk.Radiobutton(self.toolbar, text="Pencil", variable=self.tool_var, value="brush", bg="#e0e0e0", command=self.set_tool).pack(anchor="w", padx=20)
        tk.Radiobutton(self.toolbar, text="Bucket Fill", variable=self.tool_var, value="bucket", bg="#e0e0e0", command=self.set_tool).pack(anchor="w", padx=20)
        tk.Radiobutton(self.toolbar, text="Eraser (Entities)", variable=self.tool_var, value="eraser", bg="#e0e0e0", command=self.set_tool).pack(anchor="w", padx=20)

        # Tabs for layers
        tk.Label(self.toolbar, text="   LAYERS   ", bg="#e0e0e0", font=("Arial", 9, "bold")).pack(pady=(15, 5))
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self.handler.on_tab_change)

        # Tab 1: Terrain
        page_terrain = tk.Frame(self.notebook)
        self.notebook.add(page_terrain, text='Terrain')
        
        canvas_t = tk.Canvas(page_terrain, bg="#e0e0e0")
        scroll_t = tk.Scrollbar(page_terrain, orient="vertical", command=canvas_t.yview)
        scroll_frame_t = tk.Frame(canvas_t, bg="#e0e0e0")
        
        scroll_frame_t.bind("<Configure>", lambda e: canvas_t.configure(scrollregion=canvas_t.bbox("all")))
        canvas_t.create_window((0, 0), window=scroll_frame_t, anchor="nw")
        canvas_t.configure(yscrollcommand=scroll_t.set)
        
        canvas_t.pack(side="left", fill="both", expand=True)
        scroll_t.pack(side="right", fill="y")

        for t in TERRAIN_TYPES:
            b = tk.Button(
                scroll_frame_t, 
                text=f"{t['symbol']} {t['name']}", 
                bg=t['color'], fg=t['fg'], 
                anchor="w",
                command=lambda x=t: self.select_terrain(x)
            )

            b.pack(fill=tk.X, pady=1)

        # Tab 2: Entities
        page_entities = tk.Frame(self.notebook)
        self.notebook.add(page_entities, text='Entities')
        
        for e in ENTITY_TYPES:
            b = tk.Button(
                page_entities, 
                text=f"{e['name']}", 
                bg=e['color'], fg="black", 
                anchor="w",
                command=lambda x=e: self.select_entity(x)
            )
            
            b.pack(fill=tk.X, pady=1)

        # Right: Canvas
        self.canvas_frame = tk.Frame(self, bg="gray")
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)

        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg="#202020", 
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )
        
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)
        
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.handler.on_click)
        self.canvas.bind("<B1-Motion>", self.handler.on_drag)
        self.canvas.bind("<Button-3>", self.handler.on_right_click) # Eraser shortcut

    def set_tool(self):
        self.tool_type = self.tool_var.get()

    def select_terrain(self, t):
        self.current_terrain = t
        self.notebook.select(0)

    def select_entity(self, e):
        self.current_entity = e
        self.notebook.select(1)

    # Map logic:
    def prompt_new_map(self):
        # Using self.winfo_toplevel() to make sure dialogs center on the main app
        w = simpledialog.askinteger(
            "Size", 
            "Width:", 
            parent=self.winfo_toplevel(), 
            initialvalue=DEFAULT_WIDTH, 
            minvalue=10
        )

        h = simpledialog.askinteger(
            "Size",
            "Height:",
            parent=self.winfo_toplevel(),
            initialvalue=DEFAULT_HEIGHT, 
            minvalue=10
        )

        if w and h:
            self.width, self.height = w, h
            self.new_map()

    def new_map(self):
        self.map_data = [['.' for _ in range(self.width)] for _ in range(self.height)]
        self.entity_data = {}
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        self.cell_ids = []
        self.entity_ids = {}
        
        self.canvas.config(scrollregion=(0, 0, self.width * CELL_SIZE, self.height * CELL_SIZE))
        
        lookup = {t['char']: t for t in TERRAIN_TYPES}

        for y in range(self.height):
            row_ids = []
            for x in range(self.width):
                char = self.map_data[y][x]
                tile = lookup.get(char, TERRAIN_TYPES[0])
                
                x1, y1 = x * CELL_SIZE, y * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=tile['color'], outline="")

                txt = self.canvas.create_text(
                    x1 + CELL_SIZE/2,
                    y1 + CELL_SIZE/2, 
                    text=tile['symbol'], 
                    fill=tile['fg'], 
                    font=("Arial", FONT_SIZE)
                )

                row_ids.append((rect, txt))
            self.cell_ids.append(row_ids)
        
        # Redrawing entities if loading
        for coord, entity in self.entity_data.items():
            self.draw_entity_visual(coord[0], coord[1], entity)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    MapEditor(root)
    root.mainloop()