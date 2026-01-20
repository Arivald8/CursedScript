import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .cfg import CFG

class MapView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill=tk.BOTH, expand=True)

        # Rendering State
        self.cell_ids = []   # Grid IDs (rect, text)
        self.entity_ids = {} # Entity Canvas IDs {(x,y): id}

        # UI var
        self.tool_var = tk.StringVar(value="brush")
        
        self._setup_layout()
        self._setup_bindings()

    def _setup_layout(self):
        # Toolbar
        self.toolbar = tk.Frame(self, width=250, bg="#e0e0e0", relief=tk.RAISED, bd=1)
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)
        
        self._build_file_menu()
        self._build_tool_menu()
        self._build_layer_tabs()

        # Canvas area
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

    def _build_file_menu(self):
        tk.Label(self.toolbar, text=" FILE ", bg="#e0e0e0", font=("Arial", 9, "bold")).pack(pady=5)
        f = tk.Frame(self.toolbar, bg="#e0e0e0")
        f.pack(fill=tk.X, padx=5)
        tk.Button(f, text="New", command=self.controller.new_map, width=6).pack(side=tk.LEFT, padx=1)
        tk.Button(f, text="Save", command=self.controller.save_map, width=6).pack(side=tk.LEFT, padx=1)
        tk.Button(f, text="Load", command=self.controller.load_map, width=6).pack(side=tk.LEFT, padx=1)

    def _build_tool_menu(self):
        tk.Label(self.toolbar, text=" TOOLS ", bg="#e0e0e0", font=("Arial", 9, "bold")).pack(pady=(15, 5))
        modes = [("Pencil", "brush"), ("Bucket", "bucket"), ("Eraser", "eraser")]
        for text, val in modes:
            tk.Radiobutton(self.toolbar, text=text, variable=self.tool_var, value=val, 
                           bg="#e0e0e0").pack(anchor="w", padx=20)

    def _build_layer_tabs(self):
        self.notebook = ttk.Notebook(self.toolbar)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Terrain tab
        page_t = tk.Frame(self.notebook)
        self.notebook.add(page_t, text='Terrain')
        for t in CFG.TERRAIN_TYPES:
            tk.Button(page_t, text=f"{t['symbol']} {t['name']}", bg=t['color'], fg=t['fg'], anchor="w",
                      command=lambda x=t: self.controller.select_terrain(x)).pack(fill=tk.X)

        # Entity tab
        page_e = tk.Frame(self.notebook)
        self.notebook.add(page_e, text='Entities')
        for e in CFG.ENTITY_TYPES:
            tk.Button(page_e, text=e['name'], bg=e['color'], anchor="w",
                      command=lambda x=e: self.controller.select_entity(x)).pack(fill=tk.X)

    def _setup_bindings(self):
        self.canvas.bind("<Button-1>", self._handle_click)
        self.canvas.bind("<B1-Motion>", self._handle_drag)
        self.canvas.bind("<Button-3>", lambda e: self.controller.handle_click(e.x, e.y, is_right_click=True))

    def _handle_click(self, event):
        self.controller.handle_click(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def _handle_drag(self, event):
        self.controller.handle_drag(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def _on_tab_changed(self, event):
        tab = self.notebook.tab(self.notebook.select(), "text")
        self.controller.switch_layer(tab)

    # Public API for Controller -->
    def get_tool(self):
        return self.tool_var.get()
    
    def set_tool(self, val):
        self.tool_var.set(val)

    def ask_filename_save(self):
        return filedialog.asksaveasfilename(filetypes=[("Map", "*.txt")])

    def ask_filename_load(self):
        return filedialog.askopenfilename(filetypes=[("Map", "*.txt")])
    
    def show_info(self, title, msg):
        messagebox.showinfo(title, msg, parent=self)

    def show_error(self, title, msg):
        messagebox.showerror(title, msg, parent=self)
    # <-- Public API for Controller

    # Rendering -->
    def init_grid(self, width, height, map_data):
        """Full redraw of the grid structure"""
        self.canvas.delete("all")
        self.cell_ids = []
        self.entity_ids = {}
        
        self.canvas.config(scrollregion=(0, 0, width * CFG.CELL_SIZE, height * CFG.CELL_SIZE))

        for y in range(height):
            row_ids = []
            for x in range(width):
                char = map_data[y][x]
                t = CFG.get_terrain_by_char(char)
                x1, y1 = x * CFG.CELL_SIZE, y * CFG.CELL_SIZE
                
                # Draw terrain
                r = self.canvas.create_rectangle(x1, y1, x1+CFG.CELL_SIZE, y1+CFG.CELL_SIZE, fill=t['color'], outline="")
                txt = self.canvas.create_text(x1+CFG.CELL_SIZE/2, y1+CFG.CELL_SIZE/2, text=t['symbol'], fill=t['fg'])
                row_ids.append((r, txt))

            self.cell_ids.append(row_ids)

    def update_terrain_at(self, x, y, terrain_def):
        if 0 <= y < len(self.cell_ids) and 0 <= x < len(self.cell_ids[0]):
            r, txt = self.cell_ids[y][x]
            self.canvas.itemconfig(r, fill=terrain_def['color'])
            self.canvas.itemconfig(txt, text=terrain_def['symbol'], fill=terrain_def['fg'])

    def draw_entity(self, x, y, ent_def):
        # Remove old if exists
        self.remove_entity(x, y)
        
        cs = CFG.CELL_SIZE
        cx, cy = x * cs + cs/2, y * cs + cs/2
        
        if ent_def['shape'] == 'star':
            eid = self.canvas.create_oval(x*cs+2, y*cs+2, x*cs+cs-2, y*cs+cs-2, 
                                          fill=ent_def['color'], width=2)
        else:
            eid = self.canvas.create_oval(x*cs+4, y*cs+4, x*cs+cs-4, y*cs+cs-4, 
                                          fill=ent_def['color'])
            
        self.entity_ids[(x, y)] = eid

    def remove_entity(self, x, y):
        if (x, y) in self.entity_ids:
            self.canvas.delete(self.entity_ids[(x, y)])
            del self.entity_ids[(x, y)]