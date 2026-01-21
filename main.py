import os
import re
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from tools.editor.controller import Controller
from tools.theme.theme_creator import ThemeEditor


class EditorPage(ttk.Frame):
    """
    Base for all editor pages.
    """
    def __init__(self, parent, title, sub_sections):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)

        # Settings might get too long, so creating
        # a canvas and scrollbar for the content area
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Scroll
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Title
        title_label = ttk.Label(self.scrollable_frame, text=title, font=("Segoe UI", 16, "bold"))
        title_label.pack(anchor="w", pady=(20, 10), padx=20)

        # Layout shells for each sub-section
        for section in sub_sections:
            self.create_section_frame(section)

    
    def create_section_frame(self, section_name):
        """
        Creates labeled frame for a specific config group.
        """
        frame = ttk.LabelFrame(self.scrollable_frame, text=section_name, padding=10)
        frame.pack(fill="x", expand=True, padx=20, pady=5, anchor="n")

        # Placeholder
        label = ttk.Label(frame, text=f"Configuration controls for {section_name} will go here.", foreground="gray")
        label.pack(anchor="w")
        return frame
    

class CoreConfigView(ttk.Frame):
    def __init__(self, parent, project_state):
        super().__init__(parent)
        self.project_state = project_state
        
        # Title
        ttk.Label(self, text="Core Game Configuration", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=20, padx=20)

        form_frame = ttk.LabelFrame(self, text="Project Metadata", padding=15)
        form_frame.pack(fill="x", padx=20, pady=5)

        # Game Title
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

        # Instructions
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
    Special Case: Inherits directly from ttk.Frame, NOT EditorPage.
    This is because the map editor has its own full toolbar/canvas layout
    and doesn't need the generic title/scroller wrapper.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.map_controller = Controller(self)
    

class RPGConfiguratorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CursedScript Configurator")
        self.geometry("1280x800")

        # Project state
        self.state_title = tk.StringVar(value="My_New_RPG")
        self.state_author = tk.StringVar(value="Anonymous")
        self.state_version = tk.StringVar(value="0.1.0")
        self.project_state = {
            "title": self.state_title,
            "author": self.state_author,
            "version": self.state_version
        }
        # Watch for title changes to update map save path dynamically
        self.state_title.trace_add("write", self._on_title_change)

        style = ttk.Style()
        style.theme_use("clam")

        self.main_container = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=4)
        self.main_container.pack(fill="both", expand=True)

        # Left side nav
        self.sidebar_frame = ttk.Frame(self.main_container, width=250)
        self.sidebar_frame.pack_propagate(False) # Don't shrink
        self.main_container.add(self.sidebar_frame)

        label_header = ttk.Label(self.sidebar_frame, text="Configurations", font=("Arial", 10, "bold"))
        label_header.pack(pady=10, padx=5, anchor="w")

        # Nav list
        self.nav_tree = ttk.Treeview(self.sidebar_frame, show="tree", selectmode="browse")
        self.nav_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.nav_tree.bind("<<TreeviewSelect>>", self.on_nav_select)


        # Save btn
        self.btn_save_all = ttk.Button(self.sidebar_frame, text="SAVE PROJECT", command=self.save_project)
        self.btn_save_all.pack(side="bottom", fill="x", padx=10, pady=20)

        # Right content
        self.content_area = ttk.Frame(self.main_container)
        self.main_container.add(self.content_area)

        # Page instances
        self.pages = {}

        self.init_pages()
        self.init_navigation()

        first_item = self.nav_tree.get_children()[0]
        self.nav_tree.selection_set(first_item)

        # Trigger startup dialog after UI loads
        self.after(100, self.show_startup_dialog)


    def _init_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project...", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)


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

        self.btn_save_all = ttk.Button(self.sidebar_frame, text="💾 SAVE PROJECT", command=self.save_project)
        self.btn_save_all.pack(side="bottom", fill="x", padx=10, pady=20)

        # Content
        self.content_area = ttk.Frame(self.main_container)
        self.main_container.add(self.content_area)

        self.pages = {}
        self.init_pages()
        self.init_navigation()

        first_item = self.nav_tree.get_children()[0]
        self.nav_tree.selection_set(first_item)


    def init_pages(self):
        """
        Instantiates all page classes and places them in the content area grid.
        """
        # "id": (ClassReference, {kwargs_dictionary})
        page_definitions = {
            "core": (CoreConfigView, {"project_state": self.project_state}),
            "theme": (ThemeEditor, {}),
            "map": (MapEditorView, {}),
        }

        for pid, (cls, kwargs) in page_definitions.items():
            # Instantiate the page with content_area as parent, plus specific args
            page = cls(self.content_area, **kwargs)
            self.pages[pid] = page
            # Grid them all
            page.grid(row=0, column=0, sticky="nsew")

        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    
    def init_navigation(self):
        """
        Populates sidebar treeview.
        """
        nav_items = [
            ("core", "Core Configuration"),
            ("theme", "Theme/Palette"),
            ("map", "Map Editor"),
        ]

        for pid, label in nav_items:
            self.nav_tree.insert("", "end", iid=pid, text=f"  {label}")


    def on_nav_select(self, event):
        """
        Handles sidebar selection changes.
        """
        selected_items = self.nav_tree.selection()
        if not selected_items:
            return
        
        selected_id = selected_items[0]

        if selected_id in self.pages:
            self.pages[selected_id].tkraise()


    def _on_title_change(self, *args):
        """Calculates the map path based on the current title."""
        raw_title = self.state_title.get()
        safe_title = re.sub(r'[^\w\-]', '_', raw_title.replace(' ', '_'))
        if not safe_title: safe_title = "Untitled"

        base_dir = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(base_dir, "games", safe_title, "maps", "level1.json")
        
        if "map" in self.pages:
            self.pages["map"].map_controller.set_project_path(map_path)


    def show_startup_dialog(self):
        """Forces the user to choose an action on startup."""
        dialog = tk.Toplevel(self)
        dialog.title("Welcome")
        
        # Center the dialog
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
            self.state_title.set("My_New_RPG")
            self.state_author.set("Anonymous")
            self.state_version.set("0.1.0")
            
            # Reset theme
            self.pages["theme"].controller.load_sample_data()
            self.pages["theme"].controller.refresh_list()
            
            # Reset map
            self.pages["map"].map_controller.model.reset_map()
            self.pages["map"].map_controller._refresh_full_view()
            self.pages["map"].map_controller.set_project_path(None) # Disable auto-save until project is saved once
            
            self._on_title_change()

            # Go to core page
            self.pages["core"].tkraise()
            self.nav_tree.selection_set("core")

    def open_project(self):
        # Pointing to the 'games' directory
        initial_dir = os.path.join(os.path.dirname(__file__), "games")
        if not os.path.exists(initial_dir): os.makedirs(initial_dir)

        folder_path = filedialog.askdirectory(initialdir=initial_dir, title="Select Project Folder")
        if not folder_path: return

        # Check for config
        config_path = os.path.join(folder_path, "config.json")
        if not os.path.exists(config_path):
            messagebox.showerror("Error", "Not a valid project folder (missing config.json)")
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # metadata
            meta = data.get("metadata", {})
            self.state_title.set(meta.get("title", os.path.basename(folder_path)))
            self.state_author.set(meta.get("author", ""))
            self.state_version.set(meta.get("version", ""))

            # theme
            terrain = data.get("terrain", [])
            self.pages["theme"].controller.model.set_data(terrain)
            self.pages["theme"].controller.refresh_list()

            # load map, constructing the path where the map *should* be
            map_path = os.path.join(folder_path, "maps", "level1.json")
            
            # Tell map controller about this path (for future saves)
            self.pages["map"].map_controller.set_project_path(map_path)

            if os.path.exists(map_path):
                self.pages["map"].map_controller.model.load_from_disk(map_path)
                self.pages["map"].map_controller._refresh_full_view()
            else:
                # Project exists but has no map? Reset map.
                self.pages["map"].map_controller.model.reset_map()
                self.pages["map"].map_controller._refresh_full_view()

            messagebox.showinfo("Loaded", f"Project '{self.state_title.get()}' loaded successfully.")

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load project: {e}")

    def save_project(self):
        raw_title = self.state_title.get()
        # Replace spaces with underscores, remove non-alphanumeric (except _-)
        safe_title = re.sub(r'[^\w\-]', '_', raw_title.replace(' ', '_'))
        
        if not safe_title:
            messagebox.showerror("Error", "Game Title cannot be empty.")
            return

        base_path = os.path.join(os.path.dirname(__file__), "games", safe_title)
        maps_path = os.path.join(base_path, "maps")

        # Create dirs
        try:
            os.makedirs(maps_path, exist_ok=True)
        except OSError as e:
            messagebox.showerror("Error", f"Could not create directory: {e}")
            return

        # Save cfg
        try:
            terrain_data = self.pages["theme"].get_all_terrain_data()
            config_data = {
                "metadata": {
                    "title": self.state_title.get(),
                    "author": self.state_author.get(),
                    "version": self.state_version.get()
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

        # Save map
        try:
            map_view = self.pages["map"]
            map_model = map_view.map_controller.model
            map_file = os.path.join(maps_path, "level1.json")
            
            map_model.save_to_disk(map_file)
            
            # IMPORTANT: Update the Map Controller's knowledge of the file path
            # so subsequent "Save" clicks in the toolbar use this new location.
            map_view.map_controller.set_project_path(map_file)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save map file: {e}")
            return


        messagebox.showinfo("Success", f"Project saved successfully!\nLocation: {base_path}")


    def show_page(self, page_id):
        """
        Raises the selected page to the top.
        """
        if page_id in self.pages:
            self.pages[page_id].tkraise()


if __name__ == "__main__":
    app = RPGConfiguratorApp()
    app.mainloop()


