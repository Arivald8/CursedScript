import tkinter as tk
from tkinter import ttk
from tools.editor.controller import Controller as MapController

class EditorPage(ttk.Frame):
    """
    Base generic view for scrolling editor pages.
    """
    def __init__(self, parent, title, sub_sections):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        title_label = ttk.Label(self.scrollable_frame, text=title, font=("Segoe UI", 16, "bold"))
        title_label.pack(anchor="w", pady=(20, 10), padx=20)

        for section in sub_sections:
            self.create_section_frame(section)

    def create_section_frame(self, section_name):
        frame = ttk.LabelFrame(self.scrollable_frame, text=section_name, padding=10)
        frame.pack(fill="x", expand=True, padx=20, pady=5, anchor="n")
        label = ttk.Label(frame, text=f"Configuration controls for {section_name} will go here.", foreground="gray")
        label.pack(anchor="w")
        return frame


class CoreConfigView(ttk.Frame):
    """
    Specific View for editing Project Metadata.
    """
    def __init__(self, parent, project_state):
        super().__init__(parent)
        self.project_state = project_state
        
        ttk.Label(self, text="Core Game Configuration", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=20, padx=20)

        form_frame = ttk.LabelFrame(self, text="Project Metadata", padding=15)
        form_frame.pack(fill="x", padx=20, pady=5)

        # Game title
        ttk.Label(form_frame, text="Game Title (Filesystem Name):").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_title = ttk.Entry(form_frame, textvariable=self.project_state['title'])
        self.ent_title.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        ttk.Label(form_frame, text="* Used for folder name (e.g., games/My_Game_Title)", font=("Arial", 8, "italic")).grid(row=1, column=1, sticky="w")

        # Author
        ttk.Label(form_frame, text="Author:").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_author = ttk.Entry(form_frame, textvariable=self.project_state['author'])
        self.ent_author.grid(row=2, column=1, sticky="ew", pady=5, padx=10)

        # Version
        ttk.Label(form_frame, text="Version:").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_ver = ttk.Entry(form_frame, textvariable=self.project_state['version'])
        self.ent_ver.grid(row=3, column=1, sticky="ew", pady=5, padx=10)

        form_frame.columnconfigure(1, weight=1)

        info_frame = ttk.LabelFrame(self, text="Workflow Guide", padding=15)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        lbl = ttk.Label(info_frame, text=(
            "1. Set your Game Title above.\n"
            "2. Go to 'Theme/Palette' to define your ASCII characters and colors.\n"
            "3. Go to 'Map Editor' to draw your world.\n"
            "4. Click 'Save Project' in the bottom-left sidebar to write files to disk."
        ), justify="left")
        lbl.pack(anchor="w")


class MapEditorView(ttk.Frame):
    """
    Wrapper for the Map Editor Controller.
    """
    def __init__(self, parent):
        super().__init__(parent)
        # Initializes the existing Controller from tools/editor/controller.py
        self.map_controller = MapController(self)