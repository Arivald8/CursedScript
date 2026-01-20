from tkinter import filedialog, messagebox
import json
import os

class FileIO:
    def __init__(self, editor_instance, mapper_instance, terrain_types, entity_types):
        """
        :param editor_instance: Reference to the main MapEditor class
        :param terrain_types: List of dictionary definitions for terrain
        :param entity_types: List of dictionary definitions for entities
        """
        self.editor = editor_instance
        self.mapper = mapper_instance
        self.terrain_types = terrain_types
        self.entity_types = entity_types

    def save_map(self):
            filename = filedialog.asksaveasfilename(
                parent=self.editor.winfo_toplevel(), 
                defaultextension=".txt", 
                filetypes=[("Map File", "*.txt")]
            )

            if not filename: return
            
            # Saving terrain (.txt)
            try:
                with open(filename, 'w', encoding="utf-8") as f:
                    for row in self.editor.map_data:
                        f.write("".join(row) + "\n")
                
                # Save entities (.json)
                json_filename = os.path.splitext(filename)[0] + "_data.json"
                
                export_list = []
                for (x, y), data in self.editor.entity_data.items():
                    export_list.append({
                        "x": x, "y": y,
                        "type": data['type'],
                        "id": data['id']
                    })
                
                with open(json_filename, 'w', encoding="utf-8") as f:
                    json.dump(export_list, f, indent=4)
                    
                messagebox.showinfo(
                    "Saved", 
                    f"Map saved to {filename}\nEntities saved to {json_filename}",
                    parent=self.editor.winfo_toplevel()
                )
                
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self.editor.winfo_toplevel())


    def load_map(self):
        filename = filedialog.askopenfilename(
            parent=self.editor.winfo_toplevel(), 
            filetypes=[("Map File", "*.txt")]
        )

        if not filename: return
        
        try:
            # Load terrain
            with open(filename, 'r', encoding="utf-8") as f:
                lines = [line.rstrip('\n') for line in f]
            
            self.editor.height = len(lines)
            self.editor.width = max(len(l) for l in lines)
            self.editor.map_data = []
            for line in lines:
                row = list(line.ljust(self.editor.width, '.'))
                self.editor.map_data.append(row)
                
            # Load entities (if exist)
            json_filename = os.path.splitext(filename)[0] + "_data.json"
            self.editor.entity_data = {}
            
            if os.path.exists(json_filename):
                with open(json_filename, 'r') as f:
                    loaded_entities = json.load(f)
                
                # Rebuild entity dict
                entity_lookup = {e['id']: e for e in self.entity_types}
                
                for item in loaded_entities:
                    x, y = item['x'], item['y']
                    e_id = item['id']
                    if e_id in entity_lookup:
                        self.editor.entity_data[(x, y)] = entity_lookup[e_id]
            
            self.mapper.draw_grid()

            messagebox.showinfo(
                "Loaded", 
                f"Loaded map dimensions {self.editor.width}x{self.editor.height}",
                parent=self.editor.winfo_toplevel()    
            )

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.editor.winfo_toplevel())