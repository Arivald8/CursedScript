from tkinter import filedialog, messagebox
import json
import os

def save_map(editor):
        filename = filedialog.asksaveasfilename(
            parent=editor.winfo_toplevel(), 
            defaultextension=".txt", 
            filetypes=[("Map File", "*.txt")]
        )

        if not filename: return
        
        # Saving terrain (.txt)
        try:
            with open(filename, 'w', encoding="utf-8") as f:
                for row in editor.map_data:
                    f.write("".join(row) + "\n")
            
            # Save entities (.json)
            json_filename = os.path.splitext(filename)[0] + "_data.json"
            
            export_list = []
            for (x, y), data in editor.entity_data.items():
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
                parent=editor.winfo_toplevel()
            )
            
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=editor.winfo_toplevel())


def load_map(editor, ENTITY_TYPES):
    filename = filedialog.askopenfilename(
        parent=editor.winfo_toplevel(), 
        filetypes=[("Map File", "*.txt")]
    )

    if not filename: return
    
    try:
        # Load terrain
        with open(filename, 'r', encoding="utf-8") as f:
            lines = [line.rstrip('\n') for line in f]
        
        editor.height = len(lines)
        editor.width = max(len(l) for l in lines)
        editor.map_data = []
        for line in lines:
            row = list(line.ljust(editor.width, '.'))
            editor.map_data.append(row)
            
        # Load entities (if exist)
        json_filename = os.path.splitext(filename)[0] + "_data.json"
        editor.entity_data = {}
        
        if os.path.exists(json_filename):
            with open(json_filename, 'r') as f:
                loaded_entities = json.load(f)
            
            # Rebuild entity dict
            entity_lookup = {e['id']: e for e in ENTITY_TYPES}
            
            for item in loaded_entities:
                x, y = item['x'], item['y']
                e_id = item['id']
                if e_id in entity_lookup:
                    editor.entity_data[(x, y)] = entity_lookup[e_id]
        
        editor.draw_grid()
        messagebox.showinfo(
            "Loaded", 
            f"Loaded map dimensions {editor.width}x{editor.height}",
            parent=editor.winfo_toplevel()    
        )

    except Exception as e:
        messagebox.showerror("Error", str(e), parent=editor.winfo_toplevel())