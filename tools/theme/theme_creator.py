import tkinter as tk
from tkinter import ttk, colorchooser, messagebox


class ThemeModel:
    def __init__(self):
        self.terrains = []

    def set_data(self, terrain_list):
        """Load data from external source (config.json)"""
        self.terrains = terrain_list

    def get_data(self):
        """Return current data"""
        return self.terrains

    def add_terrain(self, terrain_dict):
        self.terrains.append(terrain_dict)

    def update_terrain(self, index, terrain_dict):
        if 0 <= index < len(self.terrains):
            self.terrains[index] = terrain_dict

    def delete_terrain(self, index):
        if 0 <= index < len(self.terrains):
            del self.terrains[index]

    def get_terrain(self, index):
        if 0 <= index < len(self.terrains):
            return self.terrains[index]
        return None
    
    def get_default_template(self):
        return {
            "name": "New Terrain",
            "char": "?",
            "symbol": "?",
            "color": "#FFFFFF", # Text color
            "fg": "#000000"     # Background color (based on your engine config)
        }


class ThemeView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Split: list on left, editor on right
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=4, sashrelief=tk.RAISED)
        self.paned.pack(fill="both", expand=True)

        # Left: list
        self.list_frame = ttk.Frame(self.paned, width=200)
        self.list_frame.pack_propagate(False)
        self.paned.add(self.list_frame)

        # Treeview to show terrains
        columns = ("char", "name")
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("char", text="Chr")
        self.tree.column("char", width=40, anchor="center")
        self.tree.heading("name", text="Terrain Name")
        self.tree.column("name", width=140)
        
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # right: editor
        self.editor_frame = ttk.Frame(self.paned, padding=20)
        self.paned.add(self.editor_frame)

        # Form vars
        self.var_name = tk.StringVar()
        self.var_char = tk.StringVar()
        self.var_symbol = tk.StringVar()
        self.var_color_txt = tk.StringVar(value="#FFFFFF") # Foreground/Text
        self.var_color_bg = tk.StringVar(value="#000000")  # Background

        self._create_form()
        self._create_buttons()

    def _create_form(self):
        f = self.editor_frame
        
        ttk.Label(f, text="Terrain Name:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(f, textvariable=self.var_name).grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(f, text="ASCII Char (Map Key):").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(f, textvariable=self.var_char, width=5).grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(f, text="Display Symbol (Visual):").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(f, textvariable=self.var_symbol, width=5).grid(row=2, column=1, sticky="w", pady=5)

        # Color pickers
        ttk.Label(f, text="Text Color (Hex):").grid(row=3, column=0, sticky="w", pady=5)
        c_frame1 = ttk.Frame(f)
        c_frame1.grid(row=3, column=1, sticky="w")
        ttk.Entry(c_frame1, textvariable=self.var_color_txt, width=10).pack(side="left", padx=(0,5))
        self.btn_pick_txt = tk.Button(c_frame1, text="Pick", width=4, relief="flat")
        self.btn_pick_txt.pack(side="left")

        ttk.Label(f, text="Background Color (Hex):").grid(row=4, column=0, sticky="w", pady=5)
        c_frame2 = ttk.Frame(f)
        c_frame2.grid(row=4, column=1, sticky="w")
        ttk.Entry(c_frame2, textvariable=self.var_color_bg, width=10).pack(side="left", padx=(0,5))
        self.btn_pick_bg = tk.Button(c_frame2, text="Pick", width=4, relief="flat")
        self.btn_pick_bg.pack(side="left")

        # Preview area
        ttk.Label(f, text="Preview:").grid(row=5, column=0, sticky="nw", pady=20)
        self.lbl_preview = tk.Label(f, text=" . ", font=("Consolas", 24, "bold"), relief="sunken", borderwidth=2)
        self.lbl_preview.grid(row=5, column=1, sticky="w", pady=20)

        f.columnconfigure(1, weight=1)

    def _create_buttons(self):
        b_frame = ttk.Frame(self.editor_frame)
        b_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=20)

        self.btn_new = ttk.Button(b_frame, text="New Terrain")
        self.btn_new.pack(side="left", padx=5)

        self.btn_save = ttk.Button(b_frame, text="Save / Update")
        self.btn_save.pack(side="left", padx=5)

        self.btn_delete = ttk.Button(b_frame, text="Delete")
        self.btn_delete.pack(side="right", padx=5)

    def update_preview(self):
        """Updates the large label to show what the tile looks like."""
        char = self.var_symbol.get()
        if not char: char = "?"
        fg = self.var_color_txt.get()
        bg = self.var_color_bg.get()

        try:
            self.lbl_preview.config(text=f" {char} ", fg=fg, bg=bg)
            self.btn_pick_txt.config(bg=fg)
            self.btn_pick_bg.config(bg=bg)
        except Exception:
            pass # Invalid hex code temporarily


class ThemeController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Event bindings
        self.view.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        self.view.btn_new.config(command=self.on_new)
        self.view.btn_save.config(command=self.on_save)
        self.view.btn_delete.config(command=self.on_delete)
        
        self.view.btn_pick_txt.config(command=lambda: self.pick_color('txt'))
        self.view.btn_pick_bg.config(command=lambda: self.pick_color('bg'))

        # Live preview binding
        self.view.var_symbol.trace_add("write", lambda *args: self.view.update_preview())
        self.view.var_color_txt.trace_add("write", lambda *args: self.view.update_preview())
        self.view.var_color_bg.trace_add("write", lambda *args: self.view.update_preview())

        self.load_sample_data()
        self.refresh_list()

    def load_sample_data(self):
        """
        Populates the model with a catalog of default roguelike chars.
        """
        GRASS = "#00FF00"; D_GRASS = "#006400"
        WATER = "#FFFFFF"; D_WATER = "#0000FF"
        ROAD  = "#8B4513"; D_ROAD  = "#FFFF00"
        STONE = "#808080"; D_STONE = "#202020"
        WOOD  = "#A0522D"; D_WOOD  = "#000000"

        catalogue = [
            # Standard terrain
            {"char": ".", "symbol": ".", "color": GRASS, "fg": "#000000", "name": "Grass / Floor"},
            {"char": ",", "symbol": ",", "color": "#32CD32", "fg": "#000000", "name": "Tall Grass"},
            {"char": "~", "symbol": "≈", "color": WATER, "fg": D_WATER, "name": "Water / Liquid"},
            {"char": "#", "symbol": "░", "color": ROAD, "fg": D_ROAD, "name": "Road / Path"},
            {"char": ":", "symbol": "░", "color": "#F0E68C", "fg": "#BDB76B", "name": "Sand / Dust"},
            {"char": "T", "symbol": "♠", "color": "#90EE90", "fg": D_GRASS, "name": "Tree / Forest"},
            {"char": "t", "symbol": "♣", "color": "#006400", "fg": "#000000", "name": "Small Tree / Bush"},
            {"char": "^", "symbol": "▲", "color": "#FFFFFF", "fg": "#808080", "name": "Mountain / Peak"},
            {"char": "M", "symbol": "█", "color": "#696969", "fg": "#2F4F4F", "name": "Cave / Rock"},
            
            # Structures
            {"char": "x", "symbol": "▒", "color": "#D3D3D3", "fg": "#696969", "name": "Wall (Stone)"},
            {"char": "-", "symbol": "─", "color": WOOD, "fg": D_WOOD, "name": "Wall (Horizontal)"},
            {"char": "|", "symbol": "│", "color": WOOD, "fg": D_WOOD, "name": "Wall (Vertical)"},
            {"char": "+", "symbol": "+", "color": "#FFD700", "fg": "#000000", "name": "Door / Closed"},
            {"char": "/", "symbol": "/", "color": "#FFD700", "fg": "#000000", "name": "Door / Open"},
            {"char": ">", "symbol": ">", "color": "#FFFFFF", "fg": "#000000", "name": "Stairs Down"},
            {"char": "<", "symbol": "<", "color": "#FFFFFF", "fg": "#000000", "name": "Stairs Up"},
            {"char": "O", "symbol": "⌂", "color": "#FF4500", "fg": "#000000", "name": "Building / Shrine"},
            {"char": "=", "symbol": "≡", "color": "#8B4513", "fg": "#000000", "name": "Bridge"},

            # Items / Objects
            {"char": "$", "symbol": "$", "color": "#FFD700", "fg": "#000000", "name": "Gold / Treasure"},
            {"char": "!", "symbol": "!", "color": "#FF00FF", "fg": "#000000", "name": "Potion"},
            {"char": "?", "symbol": "?", "color": "#ADFF2F", "fg": "#000000", "name": "Scroll"},
            {"char": ")", "symbol": ")", "color": "#C0C0C0", "fg": "#000000", "name": "Weapon"},
            {"char": "[", "symbol": "[", "color": "#8B4513", "fg": "#000000", "name": "Armor"},
            {"char": "*", "symbol": "*", "color": "#FF0000", "fg": "#000000", "name": "Gem / Magic"},

            # Enemies (Generic)
            {"char": "g", "symbol": "g", "color": "#32CD32", "fg": "#000000", "name": "Goblin"},
            {"char": "o", "symbol": "o", "color": "#556B2F", "fg": "#000000", "name": "Orc"},
            {"char": "D", "symbol": "D", "color": "#FF0000", "fg": "#000000", "name": "Dragon"},
            {"char": "@", "symbol": "@", "color": "#00FFFF", "fg": "#000000", "name": "Player"},
            
            # Atmospheric
            {"char": " ", "symbol": " ", "color": "#000000", "fg": "#000000", "name": "Void / Empty"},
            {"char": "_", "symbol": "_", "color": "#ADD8E6", "fg": "#000000", "name": "Ice / Fog"}
        ]

        self.model.set_data(catalogue)

    def refresh_list(self):
        # just clear tree
        for item in self.view.tree.get_children():
            self.view.tree.delete(item)
        
        # Repopulate
        for idx, item in enumerate(self.model.get_data()):
            display_str = f"[{item.get('char')}] {item.get('name')}"
            self.view.tree.insert("", "end", iid=idx, values=(item.get("char"), item.get("name")))

    def on_select(self, event):
        selected = self.view.tree.selection()
        if not selected: 
            return
        
        index = int(selected[0])

        data = self.model.get_terrain(index)

        if data:
            self.view.var_name.set(data.get("name", ""))
            self.view.var_char.set(data.get("char", ""))
            self.view.var_symbol.set(data.get("symbol", ""))
            self.view.var_color_txt.set(data.get("color", "#FFFFFF"))
            self.view.var_color_bg.set(data.get("fg", "#000000"))
            self.view.update_preview()

    def on_new(self):
        self.view.tree.selection_remove(self.view.tree.selection())
        tpl = self.model.get_default_template()
        self.view.var_name.set(tpl["name"])
        self.view.var_char.set(tpl["char"])
        self.view.var_symbol.set(tpl["symbol"])
        self.view.var_color_txt.set(tpl["color"])
        self.view.var_color_bg.set(tpl["fg"])
        self.view.update_preview()

    def on_save(self):
        data = {
            "name": self.view.var_name.get(),
            "char": self.view.var_char.get()[0] if self.view.var_char.get() else "?",
            "symbol": self.view.var_symbol.get()[0] if self.view.var_symbol.get() else "?",
            "color": self.view.var_color_txt.get(),
            "fg": self.view.var_color_bg.get()
        }

        selected = self.view.tree.selection()
        if selected:
            # Update existing
            index = int(selected[0])
            self.model.update_terrain(index, data)
        else:
            # Add new
            self.model.add_terrain(data)
        
        self.refresh_list()

    def on_delete(self):
        selected = self.view.tree.selection()
        if not selected: 
            return
        
        if messagebox.askyesno("Confirm", "Delete this terrain type?"):
            index = int(selected[0])
            self.model.delete_terrain(index)
            self.refresh_list()
            self.on_new() # Clear form

    def pick_color(self, target):
        current = self.view.var_color_txt.get() if target == 'txt' else self.view.var_color_bg.get()
        color = colorchooser.askcolor(color=current, title="Choose Color")
        if color[1]: # hex code
            if target == 'txt':
                self.view.var_color_txt.set(color[1])
            else:
                self.view.var_color_bg.set(color[1])


class ThemeEditor(ttk.Frame):
    """
    Wrapper class to be imported in main.py.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.model = ThemeModel()
        self.view = ThemeView(self)
        self.view.pack(fill="both", expand=True)
        self.controller = ThemeController(self.model, self.view)

    def get_all_terrain_data(self):
        """Used by main.py to save config.json"""
        return self.model.get_data()