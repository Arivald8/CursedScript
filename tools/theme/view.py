import tkinter as tk
from tkinter import ttk

class ThemeView(ttk.Frame):
    """
    Tkinter-based UI component for the editor with split-pane layout;
    left-side terrain list (Treeview) and a right-side property editor. 
        
    Includes colour pickers, text inputs for char/symbol definitions, and a live preview panel. 
    Handles all visual rendering and user interaction widgets.
    """

    def __init__(self, parent):
        super().__init__(parent)
        
        # Split: list on left, editor on right
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=4, sashrelief=tk.RAISED)
        self.paned.pack(fill="both", expand=True)

        # Left: list
        self.list_frame = ttk.Frame(self.paned, width=200)
        self.list_frame.pack_propagate(False)
        self.paned.add(self.list_frame)

        # Treeview to show terrains
        columns = ("char", "name")
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("char", text="Chr")
        self.tree.column("char", width=40, anchor="center")
        self.tree.heading("name", text="Terrain Name")
        self.tree.column("name", width=140)
        
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # right: editor
        self.editor_frame = ttk.Frame(self.paned, padding=20)
        self.paned.add(self.editor_frame)

        # Form vars
        self.var_name = tk.StringVar()
        self.var_char = tk.StringVar()
        self.var_symbol = tk.StringVar()
        self.var_color_txt = tk.StringVar(value="#FFFFFF") # Foreground/Text
        self.var_color_bg = tk.StringVar(value="#000000")  # Background

        self._create_form()
        self._create_buttons()

    def _create_form(self):
        f = self.editor_frame
        
        ttk.Label(f, text="Terrain Name:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(f, textvariable=self.var_name).grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(f, text="ASCII Char (Map Key):").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(f, textvariable=self.var_char, width=5).grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(f, text="Display Symbol (Visual):").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(f, textvariable=self.var_symbol, width=5).grid(row=2, column=1, sticky="w", pady=5)

        # Color pickers
        ttk.Label(f, text="Background Color (Hex):").grid(row=3, column=0, sticky="w", pady=5)
        c_frame1 = ttk.Frame(f)
        c_frame1.grid(row=3, column=1, sticky="w")
        ttk.Entry(c_frame1, textvariable=self.var_color_txt, width=10).pack(side="left", padx=(0,5))
        self.btn_pick_txt = tk.Button(c_frame1, text="Pick", width=4, relief="flat")
        self.btn_pick_txt.pack(side="left")

        ttk.Label(f, text="Entity Color (Hex):").grid(row=4, column=0, sticky="w", pady=5)
        c_frame2 = ttk.Frame(f)
        c_frame2.grid(row=4, column=1, sticky="w")
        ttk.Entry(c_frame2, textvariable=self.var_color_bg, width=10).pack(side="left", padx=(0,5))
        self.btn_pick_bg = tk.Button(c_frame2, text="Pick", width=4, relief="flat")
        self.btn_pick_bg.pack(side="left")

        # Preview area
        ttk.Label(f, text="Preview:").grid(row=5, column=0, sticky="nw", pady=20)
        self.lbl_preview = tk.Label(f, text=" . ", font=("Consolas", 24, "bold"), relief="sunken", borderwidth=2)
        self.lbl_preview.grid(row=5, column=1, sticky="w", pady=20)

        f.columnconfigure(1, weight=1)

    def _create_buttons(self):
        b_frame = ttk.Frame(self.editor_frame)
        b_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=20)

        self.btn_new = ttk.Button(b_frame, text="New Terrain")
        self.btn_new.pack(side="left", padx=5)

        self.btn_save = ttk.Button(b_frame, text="Save / Update")
        self.btn_save.pack(side="left", padx=5)

        self.btn_delete = ttk.Button(b_frame, text="Delete")
        self.btn_delete.pack(side="right", padx=5)

    def update_preview(self):
        """Updates the large label to show what the tile looks like."""
        char = self.var_symbol.get()
        if not char: char = "?"
        fg = self.var_color_txt.get()
        bg = self.var_color_bg.get()

        try:
            self.lbl_preview.config(text=f" {char} ", fg=fg, bg=bg)
            self.btn_pick_txt.config(bg=fg)
            self.btn_pick_bg.config(bg=bg)
        except Exception:
            pass # Invalid hex code temporarily
