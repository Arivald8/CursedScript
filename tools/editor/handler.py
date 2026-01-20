class Handler:
    def __init__(self, editor_instance, painter_instance, notebook_instance, tool_var_instance, cell_size):
        """
        :param editor_instance: Reference to the main MapEditor class
        :param painter_instance: Reference to Painter class
        :param notebook_instance: Reference to ttk.Notebook class
        :param tool_var_instance: Reference to tk.StringVar class
        :param cell_size: Int
        """
        self.editor = editor_instance
        self.painter = painter_instance
        self.notebook = notebook_instance
        self.tool_var = tool_var_instance
        self.cell_size = cell_size

    def get_cell_coords(self, event):
        cs = self.cell_size
        cx = self.editor.canvas.canvasx(event.x)
        cy = self.editor.canvas.canvasy(event.y)
        col = int(cx // cs)
        row = int(cy // cs)
        return col, row
    
    def set_tool(self):
        """Updates editor's tool type based on the RadioButton var."""
        self.editor.tool_type = self.tool_var.get()

    def select_terrain(self, t):
        """Sets current terrain and forces the Notebook tab to Terrain."""
        self.editor.current_terrain = t
        self.notebook.select(0)

    def select_entity(self, e):
        """Sets current entity and forces the Notebook tab to Entities."""
        self.editor.current_entity = e
        self.notebook.select(1)

    def on_click(self, event):
        x, y = self.get_cell_coords(event)
        if 0 <= x < self.editor.width and 0 <= y < self.editor.height:
            if self.editor.selected_mode == "terrain":
                if self.editor.tool_type == "bucket":
                    self.editor.painter.bucket_fill(x, y, self.editor.current_terrain)
                else:
                    self.painter.paint_terrain(x, y)
            elif self.editor.selected_mode == "entity":
                if self.editor.tool_type == "eraser":
                    self.painter.erase_entity(x, y)
                else:
                    self.painter.paint_entity(x, y)

    def on_drag(self, event):
        x, y = self.get_cell_coords(event)
        if 0 <= x < self.editor.width and 0 <= y < self.editor.height:
            if self.editor.selected_mode == "terrain" and self.editor.tool_type == "brush":
                self.painter.paint_terrain(x, y)
            elif self.editor.selected_mode == "entity" and self.editor.tool_type == "brush":
                self.painter.paint_entity(x, y)
            elif self.editor.selected_mode == "entity" and self.editor.tool_type == "eraser":
                self.painter.erase_entity(x, y)

    def on_right_click(self, event):
        # Quick erase entity
        x, y = self.get_cell_coords(event)
        self.painter.erase_entity(x, y)

    def on_tab_change(self, event):
        # try: just to handle cases where notebook isn't fully initialised
        try:
            tab_name = self.notebook.tab(self.notebook.select(), "text")
            if tab_name == "Terrain":
                self.editor.selected_mode = "terrain"
                if self.editor.tool_type == "eraser": self.tool_var.set("brush"); self.set_tool()
            else:
                self.editor.selected_mode = "entity"
                if self.editor.tool_type == "bucket": self.tool_var.set("brush"); self.set_tool() # No bucket for entities
        except:
            pass