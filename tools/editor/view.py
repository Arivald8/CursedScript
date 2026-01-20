import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .cfg import CFG

class MapView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill=tk.BOTH, expand=True)

        # Rendering State
        # Storing the IDs in a 1D list for rows, containing lists of cells
        self.cell_matrix = []
        self.rows = 0
        self.cols = 0

        # Entity tracking: {(x, y): canvas_id}
        self.entity_ids = {}

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
            xscrollcommand=self.h_scroll.set,
            xscrollincrement=1,
            yscrollincrement=1
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
            tk.Radiobutton(
                self.toolbar, 
                text=text, 
                variable=self.tool_var, 
                value=val, 
                bg="#e0e0e0"
            ).pack(anchor="w", padx=20)

    def _build_layer_tabs(self):
        self.notebook = ttk.Notebook(self.toolbar)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Terrain tab
        page_t = tk.Frame(self.notebook)
        self.notebook.add(page_t, text='Terrain')

        # Canvas scroll for terrain list
        c_frame = tk.Canvas(page_t, bg="#e0e0e0", highlightthickness=0)
        scr_bar = tk.Scrollbar(page_t, orient="vertical", command=c_frame.yview)
        inner_frame = tk.Frame(c_frame, bg="#e0e0e0")

        inner_frame.bind("<Configure>", lambda e: c_frame.configure(scrollregion=c_frame.bbox("all")))
        c_frame.create_window((0,0), window=inner_frame, anchor="nw")
        c_frame.configure(yscrollcommand=scr_bar.set)
        
        c_frame.pack(side="left", fill="both", expand=True)
        scr_bar.pack(side="right", fill="y")


        for t in CFG.TERRAIN_TYPES:
            tk.Button(
                page_t, 
                text=f"{t['symbol']} {t['name']}", 
                bg=t['color'], fg=t['fg'], 
                anchor="w",
                command=lambda x=t: self.controller.select_terrain(x)
            ).pack(fill=tk.X, pady=1)

        # Entity tab
        page_e = tk.Frame(self.notebook)
        self.notebook.add(page_e, text='Entities')
        for e in CFG.ENTITY_TYPES:
            tk.Button(
                page_e, 
                text=e['name'],
                bg=e['color'], 
                anchor="w",
                command=lambda x=e: self.controller.select_entity(x)
            ).pack(fill=tk.X, pady=1)

    def _setup_bindings(self):
        self.canvas.bind("<Button-1>", self._handle_click)
        self.canvas.bind("<B1-Motion>", self._handle_drag)
        self.canvas.bind("<Button-3>", lambda e: self.controller.handle_click(e.x, e.y, is_right_click=True))

    def _handle_click(self, event):
        self.controller.handle_click(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def _handle_drag(self, event):
        self.controller.handle_drag(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def _on_tab_changed(self, event):
        if self.notebook.select():
            tab = self.notebook.tab(self.notebook.select(), "text")
            self.controller.switch_layer(tab)

    # Public API for Controller -->
    def get_tool(self):
        return self.tool_var.get()
    
    def set_tool(self, val):
        self.tool_var.set(val)

    def ask_filename_save(self):
        return filedialog.asksaveasfilename(
            parent=self, 
            defaultextension=".json",
            filetypes=[("Map JSON", "*.json"), ("All Files", "*.*")]
        )

    def ask_filename_load(self):
        return filedialog.askopenfilename(
            parent=self, 
            filetypes=[("Map JSON", "*.json"), ("All Files", "*.*")]
        )
    
    def show_info(self, title, msg):
        messagebox.showinfo(title, msg, parent=self)

    def show_error(self, title, msg):
        messagebox.showerror(title, msg, parent=self)
    # <-- Public API for Controller

    # Rendering -->
    def init_grid(self, width, height, map_data):
        """
        If the grid size is the same as before, we reuse the existing canvas items
        (object pooling) instead of destroying and recreating them.
        """
        px_w = width * CFG.CELL_SIZE
        px_h = height * CFG.CELL_SIZE
        self.canvas.config(scrollregion=(0, 0, px_w, px_h))

        # Check if full rebuild is needed
        full_rebuild = (width != self.cols or height != self.rows)

        if full_rebuild:
            self.canvas.delete("all")
            self.cell_matrix = []
            self.entity_ids = {} # Entities must be cleared on resize
            self.rows = height
            self.cols = width

            # Create new grid
            for y in range(height):
                row_list = []
                for x in range(width):
                    x1, y1 = x * CFG.CELL_SIZE, y * CFG.CELL_SIZE

                    r = self.canvas.create_rectangle(
                        x1, 
                        y1, 
                        x1+CFG.CELL_SIZE, 
                        y1+CFG.CELL_SIZE,
                        outline="",
                        tags=("terrain", f"row_{y}", f"col_{x}")
                    )

                    t = self.canvas.create_text(
                        x1+CFG.CELL_SIZE/2, 
                        y1+CFG.CELL_SIZE/2, 
                        font=("Arial", CFG.FONT_SIZE),
                        tags=("terrain_txt", f"row_{y}", f"col_{x}")
                    )

                    row_list.append({"rect": r, "text": t})
                self.cell_matrix.append(row_list)
        else:
            # Grid size is the same, just clear entities.
            # Using tab 'entity' to delete all creatures/items
            self.canvas.delete("entity")
            self.entity_ids = {}

        # Apply data to grid (batch update)
        for y in range(height):
            for x in range(width):
                char = map_data[y][x]
                t_def = CFG.get_terrain_by_char(char)
                self.update_terrain_at(x, y, t_def)


    def update_terrain_at(self, x, y, terrain_def):
        """Updates a specific cell's visual appearance."""
        if 0 <= y < self.rows and 0 <= x < self.cols:
            cell = self.cell_matrix[y][x]
            self.canvas.itemconfig(cell['rect'], fill=terrain_def['color'])
            self.canvas.itemconfig(cell['text'], text=terrain_def['symbol'], fill=terrain_def['fg'])


    def draw_entity(self, x, y, ent_def):
        # Remove old if exists
        self.remove_entity(x, y)
        
        cs = CFG.CELL_SIZE

        # Padding
        p = 2 
        x1, y1 = x * cs + p, y * cs + p
        x2, y2 = x * cs + cs - p, y * cs + cs - p
        
        tags = ("entity", f"ent_{x}_{y}")

        if ent_def['shape'] == 'star':
            # simplified
            eid = self.canvas.create_oval(x1, y1, x2, y2, fill=ent_def['color'], width=2, tags=tags)
        elif ent_def['shape'] == 'diamond':
            cx, cy = x * cs + cs/2, y * cs + cs/2
            offset = cs/2 - 2
            eid = self.canvas.create_polygon(
                cx, 
                cy-offset, 
                cx+offset, 
                cy, 
                cx, 
                cy+offset, 
                cx-offset, 
                cy, 
                fill=ent_def['color'], outline="black", tags=tags
            )
        else:
            eid = self.canvas.create_oval(x1+2, y1+2, x2-2, y2-2, fill=ent_def['color'], tags=tags)
            
        self.entity_ids[(x, y)] = eid

    def remove_entity(self, x, y):
        if (x, y) in self.entity_ids:
            self.canvas.delete(self.entity_ids[(x, y)])
            del self.entity_ids[(x, y)]