import os
import re
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from tools.theme.theme_creator import ThemeEditor
from tools.configurator.view import CoreConfigView, MapEditorView
from tools.configurator.model import ProjectModel

class RPGConfiguratorApp(tk.Tk):
    """
    The Main Controller for the Configurator Tool.
    """
    def __init__(self, root_path):
        super().__init__()
        
        self.root_path = root_path
        self.title("CursedScript Configurator")
        self.geometry("1280x800")

        self.model = ProjectModel()
        
        # Watch for title changes to update map save path dynamically
        self.model.title.trace_add("write", self._on_title_change)

        self._init_ui()
        
        # Trigger startup dialog after UI loads
        self.after(100, self.show_startup_dialog)

    def _init_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        self.main_container = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=4)
        self.main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar_frame = ttk.Frame(self.main_container, width=250)
        self.sidebar_frame.pack_propagate(False) 
        self.main_container.add(self.sidebar_frame)

        label_header = ttk.Label(self.sidebar_frame, text="Configurations", font=("Arial", 10, "bold"))
        label_header.pack(pady=10, padx=5, anchor="w")

        self.nav_tree = ttk.Treeview(self.sidebar_frame, show="tree", selectmode="browse")
        self.nav_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.nav_tree.bind("<<TreeviewSelect>>", self.on_nav_select)

        self.btn_save_all = ttk.Button(self.sidebar_frame, text="SAVE PROJECT", command=self.save_project)
        self.btn_save_all.pack(side="bottom", fill="x", padx=10, pady=20)

        # Content area
        self.content_area = ttk.Frame(self.main_container)
        self.main_container.add(self.content_area)

        self.pages = {}
        self.init_pages()
        self.init_navigation()

        first_item = self.nav_tree.get_children()[0]
        self.nav_tree.selection_set(first_item)

    def init_pages(self):
        # "id": (ClassReference, {kwargs})
        page_definitions = {
            "core": (CoreConfigView, {"project_state": self.model.get_state_dict()}),
            "theme": (ThemeEditor, {}),
            "map": (MapEditorView, {}),
        }

        for pid, (cls, kwargs) in page_definitions.items():
            page = cls(self.content_area, **kwargs)
            self.pages[pid] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    def init_navigation(self):
        nav_items = [
            ("core", "Core Configuration"),
            ("theme", "Theme/Palette"),
            ("map", "Map Editor"),
        ]
        for pid, label in nav_items:
            self.nav_tree.insert("", "end", iid=pid, text=f"  {label}")

    def on_nav_select(self, event):
        selected_items = self.nav_tree.selection()
        if not selected_items: return
        
        selected_id = selected_items[0]
        if selected_id in self.pages:
            self.pages[selected_id].tkraise()

    def _on_title_change(self, *args):
        """Calculates the map path based on the current title."""
        raw_title = self.model.title.get()
        safe_title = re.sub(r'[^\w\-]', '_', raw_title.replace(' ', '_'))
        if not safe_title: safe_title = "Untitled"

        map_path = os.path.join(self.root_path, "games", safe_title, "maps", "level1.json")
        
        if "map" in self.pages:
            self.pages["map"].map_controller.set_project_path(map_path)

    def show_startup_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Welcome")
        dialog.transient(self)
        dialog.grab_set()
        
        x = self.winfo_x() + (self.winfo_width() // 2) - 150
        y = self.winfo_y() + (self.winfo_height() // 2) - 75
        dialog.geometry(f"300x150+{x}+{y}")

        ttk.Label(dialog, text="CursedScript Configurator", font=("Arial", 12, "bold")).pack(pady=10)
        
        def do_new():
            dialog.destroy()
            self.new_project()
        
        def do_open():
            dialog.destroy()
            self.open_project()

        ttk.Button(dialog, text="New Project", command=do_new).pack(fill="x", padx=20, pady=5)
        ttk.Button(dialog, text="Open Existing Project", command=do_open).pack(fill="x", padx=20, pady=5)
        dialog.protocol("WM_DELETE_WINDOW", self.quit)

    def new_project(self):
        if messagebox.askyesno("New Project", "Discard current changes and start new?"):
            self.model.reset()
            
            # Reset theme
            self.pages["theme"].controller.load_sample_data()
            self.pages["theme"].controller.refresh_list()
            
            # Reset map
            self.pages["map"].map_controller.model.reset_map()
            self.pages["map"].map_controller._refresh_full_view()
            self.pages["map"].map_controller.set_project_path(None)
            
            self._on_title_change()
            self.pages["core"].tkraise()
            self.nav_tree.selection_set("core")

    def open_project(self):
        initial_dir = os.path.join(self.root_path, "games")
        if not os.path.exists(initial_dir): os.makedirs(initial_dir)

        folder_path = filedialog.askdirectory(initialdir=initial_dir, title="Select Project Folder")
        if not folder_path: return

        config_path = os.path.join(folder_path, "config.json")
        if not os.path.exists(config_path):
            messagebox.showerror("Error", "Not a valid project folder (missing config.json)")
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load metadata into Model
            self.model.load_from_dict(data.get("metadata", {}))
            # Manually set title if missing to match folder name
            if not data.get("metadata", {}).get("title"):
                self.model.title.set(os.path.basename(folder_path))

            # Load theme
            terrain = data.get("terrain", [])
            self.pages["theme"].controller.model.set_data(terrain)
            self.pages["theme"].controller.refresh_list()

            # Load map
            map_path = os.path.join(folder_path, "maps", "level1.json")
            self.pages["map"].map_controller.set_project_path(map_path)

            if os.path.exists(map_path):
                self.pages["map"].map_controller.model.load_from_disk(map_path)
                self.pages["map"].map_controller._refresh_full_view()
            else:
                self.pages["map"].map_controller.model.reset_map()
                self.pages["map"].map_controller._refresh_full_view()

            messagebox.showinfo("Loaded", f"Project '{self.model.title.get()}' loaded successfully.")

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load project: {e}")

    def save_project(self):
        raw_title = self.model.title.get()
        safe_title = re.sub(r'[^\w\-]', '_', raw_title.replace(' ', '_'))
        
        if not safe_title:
            messagebox.showerror("Error", "Game Title cannot be empty.")
            return

        base_path = os.path.join(self.root_path, "games", safe_title)
        maps_path = os.path.join(base_path, "maps")

        try:
            os.makedirs(maps_path, exist_ok=True)
        except OSError as e:
            messagebox.showerror("Error", f"Could not create directory: {e}")
            return

        # Save Config
        try:
            terrain_data = self.pages["theme"].get_all_terrain_data()
            config_data = {
                "metadata": {
                    "title": self.model.title.get(),
                    "author": self.model.author.get(),
                    "version": self.model.version.get()
                },
                "settings": {"default_width": 60, "default_height": 40, "cell_size": 20},
                "terrain": terrain_data,
                "entities": [{"type": "player", "id": "player_start", "name": "Player Start", "color": "#FFFFFF", "shape": "star"}]
            }

            with open(os.path.join(base_path, "config.json"), 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config.json: {e}")
            return

        # Save Map
        try:
            map_view = self.pages["map"]
            map_model = map_view.map_controller.model
            map_file = os.path.join(maps_path, "level1.json")
            
            map_model.save_to_disk(map_file)
            map_view.map_controller.set_project_path(map_file)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save map file: {e}")
            return

        messagebox.showinfo("Success", f"Project saved successfully!\nLocation: {base_path}")