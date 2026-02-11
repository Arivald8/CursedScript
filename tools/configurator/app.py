import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from tools.theme.theme_creator import ThemeEditor
from tools.configurator.view import CoreConfigView, MapEditorView
from tools.configurator.model import ProjectModel
from tools.configurator.storage import ProjectStorage

class RPGConfiguratorApp(tk.Tk):
    """
    Purely a 'Manager' class. Asks the View for data, gives it to Storage
    to save, and updates the Model.
    """
    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        self.title("CursedScript Configurator")
        self.geometry("1280x800")

        self.model = ProjectModel()
        self.model.title.trace_add("write", self._on_title_change)

        self._init_ui()
        self.after(100, self.show_startup_dialog)

    def _init_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        self.main_container = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=4)
        self.main_container.pack(fill="both", expand=True)

        self.sidebar_frame = ttk.Frame(self.main_container, width=250)
        self.sidebar_frame.pack_propagate(False) 
        self.main_container.add(self.sidebar_frame)

        ttk.Label(self.sidebar_frame, text="Configurations", font=("Arial", 10, "bold")).pack(pady=10, padx=5, anchor="w")

        self.nav_tree = ttk.Treeview(self.sidebar_frame, show="tree", selectmode="browse")
        self.nav_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.nav_tree.bind("<<TreeviewSelect>>", self.on_nav_select)

        self.btn_save_all = ttk.Button(self.sidebar_frame, text="SAVE PROJECT", command=self.save_project)
        self.btn_save_all.pack(side="bottom", fill="x", padx=10, pady=20)

        self.content_area = ttk.Frame(self.main_container)
        self.main_container.add(self.content_area)

        self.pages = {}
        self.init_pages()
        self.init_navigation()
        self.nav_tree.selection_set(self.nav_tree.get_children()[0])

    def init_pages(self):
        self.pages["core"] = CoreConfigView(self.content_area, project_state=self.model.get_state_dict())
        
        self.pages["theme"] = ThemeEditor(
            self.content_area,
            on_theme_change=self.sync_theme_to_map
        )
        
        self.pages["map"] = MapEditorView(self.content_area)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    def init_navigation(self):
        self.nav_tree.insert("", "end", iid="core", text="  Core Configuration")
        self.nav_tree.insert("", "end", iid="theme", text="  Theme/Palette")
        self.nav_tree.insert("", "end", iid="map", text="  Map Editor")

    def sync_theme_to_map(self, terrain_data):
        """Bridge function: Theme Editor -> Map Editor"""
        if "map" in self.pages:
            self.pages["map"].map_controller.sync_terrain_data(terrain_data)

    def on_nav_select(self, event):
        sel = self.nav_tree.selection()
        if sel and sel[0] in self.pages:
            self.pages[sel[0]].tkraise()

    def _on_title_change(self, *args):
        safe_title = ProjectStorage.get_safe_title(self.model.title.get())
        map_path = os.path.join(self.root_path, "games", safe_title, "maps", "level1.json")
        self.pages["map"].map_controller.set_project_path(map_path)

    def new_project(self):
        if not messagebox.askyesno("New Project", "Discard current changes?"): 
            return
        
        self.model.reset()
        self.pages["theme"].controller.load_sample_data()
        self.pages["theme"].controller.refresh_list()
        self.pages["map"].map_controller.model.reset_map()
        self.pages["map"].map_controller._refresh_full_view()
        self._on_title_change() # Updates paths
        
        self.pages["core"].tkraise()
        self.nav_tree.selection_set("core")

    def open_project(self):
        initial_dir = os.path.join(self.root_path, "games")
        folder_path = filedialog.askdirectory(initialdir=initial_dir, title="Select Project Folder")
        
        if not folder_path: 
            return
        
        try:
            data = ProjectStorage.load_config(folder_path)
            
            # Update UI/Model
            self.model.load_from_dict(data.get("metadata", {}))
            if not data.get("metadata", {}).get("title"):
                self.model.title.set(os.path.basename(folder_path))

            terrain_data = data.get("terrain", [])

            self.pages["theme"].controller.model.set_data(terrain_data)
            self.pages["theme"].controller.refresh_list()

            self.sync_theme_to_map(terrain_data)

            # Handle map
            map_path = os.path.join(folder_path, "maps", "level1.json")
            self.pages["map"].map_controller.set_project_path(map_path)
            
            if os.path.exists(map_path):
                self.pages["map"].map_controller.model.load_from_disk(map_path)
            else:
                self.pages["map"].map_controller.model.reset_map()
            
            self.pages["map"].map_controller._refresh_full_view()
            messagebox.showinfo("Loaded", f"Project '{self.model.title.get()}' loaded.")

        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def save_project(self):
        if not self.model.title.get():
            messagebox.showerror("Error", "Game Title cannot be empty.")
            return

        safe_title = ProjectStorage.get_safe_title(self.model.title.get())
        base_path = os.path.join(self.root_path, "games", safe_title)

        try:
            maps_path = ProjectStorage.create_project_structure(base_path)

            # Save cfg
            terrain_data = self.pages["theme"].get_all_terrain_data()
            meta_data = self.model.get_state_dict() # returns tk.StringVars
            # Convert vars to strings for storage
            meta_clean = {k: v.get() for k, v in meta_data.items()}
            
            ProjectStorage.save_config(base_path, meta_clean, terrain_data)

            # map save delegated to map controller)
            map_file = os.path.join(maps_path, "level1.json")
            self.pages["map"].map_controller.model.save_to_disk(map_file)
            self.pages["map"].map_controller.set_project_path(map_file)

            messagebox.showinfo("Success", f"Project saved to:\n{base_path}")

        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def show_startup_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Welcome")
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - 150
        y = self.winfo_y() + (self.winfo_height() // 2) - 75
        dialog.geometry(f"300x150+{x}+{y}")
        
        ttk.Label(dialog, text="CursedScript Configurator", font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Button(dialog, text="New Project", command=lambda: [dialog.destroy(), self.new_project()]).pack(fill="x", padx=20, pady=5)
        ttk.Button(dialog, text="Open Project", command=lambda: [dialog.destroy(), self.open_project()]).pack(fill="x", padx=20, pady=5)
        
        dialog.protocol("WM_DELETE_WINDOW", self.quit)
        dialog.transient(self)
        dialog.grab_set()



        