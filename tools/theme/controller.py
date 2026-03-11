from tkinter import colorchooser, messagebox

class ThemeController:
    """
    Coordinates ThemeModel and ThemeView, handling user interaction.
    
    Also handles terrain selection, creation, updating, deletion, and colour picking operations,
    providing callback integration for theme updates to external systems.
    """
    def __init__(self, model, view, on_update_callback=None):
        self.model = model
        self.view = view
        self.on_update_callback = on_update_callback

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

        if self.on_update_callback:
            # Sending the full updates list to the main app
            self.on_update_callback(self.model.get_data())

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
