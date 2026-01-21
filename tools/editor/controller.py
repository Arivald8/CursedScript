import os
import tkinter as tk
from tkinter import simpledialog
from .cfg import CFG
from .model import MapModel
from .view import MapView


class Controller:
    def __init__(self, root):
        self.root = root
        self.model = MapModel()
        self.view = MapView(root, self)
        
        # App state
        self.current_layer = "Terrain" # or "Entities"
        self.selected_terrain = CFG.TERRAIN_TYPES[0]
        self.selected_entity = CFG.ENTITY_TYPES[0]

        # Project integration state
        self.fixed_save_path = None
        
        # Initial draw
        self._refresh_full_view()

    def set_project_path(self, path):
        """
        Called by main app when a project is loaded or saved.
        Sets the target for 'level1.json'
        """
        self.fixed_save_path = path

    def sync_terrain_data(self, terrain_data):
        """
        Updates the CFG with new terrain definitions from the Theme Editor
        and redraws the current map to reflect changes immediately.
        """
        CFG.update_terrain_data(terrain_data)
        self.view.refresh_terrain_sidebar()
        self._refresh_full_view()

    def _refresh_full_view(self):
        self.view.init_grid(self.model.width, self.model.height, self.model.map_data)
        for (x, y), ent in self.model.entity_data.items():
            self.view.draw_entity(x, y, ent)

    # User actions -->
    def handle_click(self, canvas_x, canvas_y, is_right_click=False):
        col = int(canvas_x // CFG.CELL_SIZE)
        row = int(canvas_y // CFG.CELL_SIZE)
        
        if is_right_click:
            # Right click always erases entity
            self._erase_entity(col, row)
            return

        tool = self.view.get_tool()
        
        if self.current_layer == "Terrain":
            if tool == "bucket":
                self._apply_bucket(col, row)
            else:
                self._apply_terrain(col, row)
        
        elif self.current_layer == "Entities":
            if tool == "eraser":
                self._erase_entity(col, row)
            elif tool == "bucket":
                pass # No bucket for entities
            else:
                self._place_entity(col, row)

    def handle_drag(self, canvas_x, canvas_y):
        col = int(canvas_x // CFG.CELL_SIZE)
        row = int(canvas_y // CFG.CELL_SIZE)
        tool = self.view.get_tool()

        if tool == "brush":
            if self.current_layer == "Terrain":
                self._apply_terrain(col, row)
            elif self.current_layer == "Entities":
                self._place_entity(col, row)
        elif tool == "eraser" and self.current_layer == "Entities":
            self._erase_entity(col, row)
    # <-- User actions

    # Logic helpers -->
    def _apply_terrain(self, x, y):
        # Update model
        changed = self.model.set_terrain(x, y, self.selected_terrain['char'])
        # Update view
        if changed:
            self.view.update_terrain_at(x, y, self.selected_terrain)

    def _apply_bucket(self, x, y):
        # Model returns list of changed cells
        changes = self.model.bucket_fill(x, y, self.selected_terrain['char'])
        # View updates only those cells
        for cx, cy in changes:
            self.view.update_terrain_at(cx, cy, self.selected_terrain)

    def _place_entity(self, x, y):
        self.model.add_entity(x, y, self.selected_entity)
        self.view.draw_entity(x, y, self.selected_entity)

    def _erase_entity(self, x, y):
        self.model.remove_entity(x, y)
        self.view.remove_entity(x, y)
    # <-- Logic helpers

    # Toolbar callbacks -->
    def select_terrain(self, t_def):
        self.selected_terrain = t_def
        self.view.notebook.select(0) # Force tab switch
        
        
    def select_entity(self, e_def):
        self.selected_entity = e_def
        self.view.notebook.select(1) # Force tab switch


    def switch_layer(self, layer_name):
        self.current_layer = layer_name
        # Logic to auto-switch tools (e.g. disable bucket on entities)
        if layer_name == "Entities" and self.view.get_tool() == "bucket":
            self.view.set_tool("brush")


    def new_map(self):
        w = simpledialog.askinteger("New Map", "Width:", initialvalue=60, minvalue=10)
        h = simpledialog.askinteger("New Map", "Height:", initialvalue=40, minvalue=10)
        if w and h:
            self.model.resize(w, h)
            self._refresh_full_view()


    def save_map(self):
        """
        Saves automatically if part of a project, otherwise asks user.
        """
        target_file = None

        if self.fixed_save_path:
            target_file = self.fixed_save_path
            folder = os.path.dirname(target_file)
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder, exist_ok=True)
                except Exception:
                    # If permission error, force fallback to dialog
                    target_file = None

        if not target_file:
            # Fallback to dialog
            target_file = self.view.ask_filename_save()

        if target_file:
            try:
                self.model.save_to_disk(target_file)
                self.view.show_info("Map Saved", f"Successfully saved to:\n{target_file}")
            except Exception as e:
                self.view.show_error("Save Error", str(e))


    def load_map(self):
        """
        Loads project map if available, or asks user if they really want to import external.
        """
        target_file = None
        
        # If we are in a project, give choice
        if self.fixed_save_path and os.path.exists(self.fixed_save_path):
            choice = self.view.ask_yes_no_cancel(
                "Load Map", 
                "Reload the project's 'level1.json'?\n\nYes = Reload Project Map\nNo = Import External File"
            )
            if choice is True: # Yes
                target_file = self.fixed_save_path
            elif choice is False: # No
                target_file = self.view.ask_filename_load()
            else: # Cancel
                return
        else:
            target_file = self.view.ask_filename_load()

        if target_file and os.path.exists(target_file):
            try:
                self.model.load_from_disk(target_file)
                self._refresh_full_view()
                self.view.show_info("Success", "Map Loaded")
            except Exception as e:
                self.view.show_error("Load Error", str(e))
    # <-- Toolbar callbacks

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    app = Controller(root)
    root.mainloop()