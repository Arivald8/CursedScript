import tkinter as tk
from tkinter import ttk
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
    

class CoreConfigView(EditorPage):
    def __init__(self, parent):
        sub_sections = [
            "Game Metadata (Title, Author, Version)",
            "Resolution Settings (Terminal constr)",
            "Colour Palette (Schemes)",
        ]
        super().__init__(parent, "Core Game Configuration", sub_sections)


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
        self.minsize(1000, 700)

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

        # Nav list using treeview
        self.nav_tree = ttk.Treeview(self.sidebar_frame, show="tree", selectmode="browse")
        self.nav_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.nav_tree.bind("<<TreeviewSelect>>", self.on_nav_select)

        # Right content
        self.content_area = ttk.Frame(self.main_container)
        self.main_container.add(self.content_area)

        # Page instances
        self.pages = {}

        self.init_pages()
        self.init_navigation()

        first_item = self.nav_tree.get_children()[0]
        self.nav_tree.selection_set(first_item)


    def init_pages(self):
        """
        Instantiates all page classes and places them in the content area grid.
        """
        page_definitions = {
            "core": CoreConfigView,
            "map": MapEditorView,
            "theme": ThemeEditor,
        }

        for pid, cls in page_definitions.items():
            page = cls(self.content_area)
            self.pages[pid] = page
            # Stacking all pages on top of each other
            page.grid(row=0, column=0, sticky="nsew")

        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    
    def init_navigation(self):
        """
        Populates sidebar treeview.
        """
        nav_items = [
            ("core", "Core Configuration"),
            ("map", "Map Editor"),
            ("theme", "Theme/Palette")
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
        self.show_page(selected_id)


    def show_page(self, page_id):
        """
        Raises the selected page to the top.
        """
        if page_id in self.pages:
            self.pages[page_id].tkraise()


if __name__ == "__main__":
    app = RPGConfiguratorApp()
    app.mainloop()


