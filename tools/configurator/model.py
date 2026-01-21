import tkinter as tk

class ProjectModel:
    """
    Holds the reactive state of the current project.
    """
    def __init__(self):
        self.title = tk.StringVar(value="My_New_RPG")
        self.author = tk.StringVar(value="Anonymous")
        self.version = tk.StringVar(value="0.1.0")

    def get_state_dict(self):
        """Returns the state as a dictionary for the generic view classes."""
        return {
            "title": self.title,
            "author": self.author,
            "version": self.version
        }

    def reset(self):
        self.title.set("My_New_RPG")
        self.author.set("Anonymous")
        self.version.set("0.1.0")

    def load_from_dict(self, meta_dict):
        self.title.set(meta_dict.get("title", "Untitled"))
        self.author.set(meta_dict.get("author", ""))
        self.version.set(meta_dict.get("version", ""))