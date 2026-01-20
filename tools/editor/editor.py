import tkinter as tk
from tkinter import ttk
from .cfg import CFG
from .paint import Paint
from .file_io import FileIO
from .handler import Handler
from .mapper import Mapper


class MapEditor(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        
        # Data State
        self.width = CFG.DEFAULT_WIDTH
        self.height = CFG.DEFAULT_HEIGHT
        self.map_data = []          # 2D array of chars
        self.entity_data = {}       # Dict: {(x,y): EntityDict}
        
        # Used in tool manager classes 
        self.toolbar = tk.Frame(self, width=250, bg="#e0e0e0", relief=tk.RAISED, bd=1)
        self.notebook = ttk.Notebook(self.toolbar)
        self.tool_var = tk.StringVar(value="brush")
        # in mappter.py -->
        self.canvas_frame = tk.Frame(self, bg="gray")
        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg="#202020", 
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )
        # <-- in mapper.py

        # Tools State
        self.painter = Paint(self, self.canvas)
        self.handler = Handler(self, self.painter, self.notebook, self.tool_var)
        self.mapper = Mapper(self, self.handler, self.canvas)
        self.file_io = FileIO(self, self.mapper)

        self.selected_mode = "terrain" # 'terrain' or 'entity'
        self.current_terrain = CFG.TERRAIN_TYPES[0]
        self.current_entity = CFG.ENTITY_TYPES[0]
        self.tool_type = "brush"       # 'brush' or 'bucket'
        
        # Rendering State
        self.cell_ids = []          # Grid IDs (rect, text)
        self.entity_ids = {}        # Entity Canvas IDs {(x,y): id}

        self.setup_ui()
        self.mapper.new_map()

    def setup_ui(self):
        # Left: Toolbar
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)
        
        # File IO
        tk.Label(self.toolbar, text="   FILE   ", bg="#e0e0e0", font=("Arial", 9, "bold")).pack(pady=5)
        btn_frame = tk.Frame(self.toolbar, bg="#e0e0e0")
        btn_frame.pack(fill=tk.X, padx=5)

        tk.Button(btn_frame, text="New", command=self.mapper.prompt_new_map, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Save", command=self.file_io.save_map, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Load", command=self.file_io.load_map, width=8).pack(side=tk.LEFT, padx=2)

        tk.Label(self.toolbar, text="   TOOLS   ", bg="#e0e0e0", font=("Arial", 9, "bold")).pack(pady=(15, 5))
        
        # Tool select
        tk.Radiobutton(self.toolbar, text="Pencil", variable=self.tool_var, value="brush", bg="#e0e0e0", command=self.handler.set_tool).pack(anchor="w", padx=20)
        tk.Radiobutton(self.toolbar, text="Bucket Fill", variable=self.tool_var, value="bucket", bg="#e0e0e0", command=self.handler.set_tool).pack(anchor="w", padx=20)
        tk.Radiobutton(self.toolbar, text="Eraser (Entities)", variable=self.tool_var, value="eraser", bg="#e0e0e0", command=self.handler.set_tool).pack(anchor="w", padx=20)

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

        for t in CFG.TERRAIN_TYPES:
            b = tk.Button(
                scroll_frame_t, 
                text=f"{t['symbol']} {t['name']}", 
                bg=t['color'], fg=t['fg'], 
                anchor="w",
                command=lambda x=t: self.handler.select_terrain(x)
            )

            b.pack(fill=tk.X, pady=1)

        # Tab 2: Entities
        page_entities = tk.Frame(self.notebook)
        self.notebook.add(page_entities, text='Entities')
        
        for e in CFG.ENTITY_TYPES:
            b = tk.Button(
                page_entities, 
                text=f"{e['name']}", 
                bg=e['color'], fg="black", 
                anchor="w",
                command=lambda x=e: self.handler.select_entity(x)
            )

            b.pack(fill=tk.X, pady=1)

        # Right: Canvas
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)
        
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.handler.on_click)
        self.canvas.bind("<B1-Motion>", self.handler.on_drag)
        self.canvas.bind("<Button-3>", self.handler.on_right_click) # Eraser shortcut


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    MapEditor(root)
    root.mainloop()