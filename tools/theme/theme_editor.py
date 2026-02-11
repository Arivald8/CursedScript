from tkinter import ttk

from .view import ThemeView
from .controller import ThemeController
from .model import ThemeModel

class ThemeEditor(ttk.Frame):
    """
    Wrapper class to be imported in main.py.
    """
    def __init__(self, parent, on_theme_change=None):
        super().__init__(parent)
        self.model = ThemeModel()
        self.view = ThemeView(self)
        self.view.pack(fill="both", expand=True)
        self.controller = ThemeController(self.model, self.view, on_update_callback=on_theme_change)

    def get_all_terrain_data(self):
        """Used by main.py to save config.json"""
        return self.model.get_data()