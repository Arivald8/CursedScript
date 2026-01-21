import os
import json
import re

class ProjectStorage:
    @staticmethod
    def get_safe_title(raw_title):
        """Sanitizes the title for use as a folder name."""
        safe_title = re.sub(r'[^\w\-]', '_', raw_title.replace(' ', '_'))
        return safe_title if safe_title else "Untitled"

    @staticmethod
    def create_project_structure(base_path):
        """Ensures the directory structure exists."""
        maps_path = os.path.join(base_path, "maps")
        os.makedirs(maps_path, exist_ok=True)
        return maps_path

    @staticmethod
    def load_config(folder_path):
        """Loads and parses config.json."""
        config_path = os.path.join(folder_path, "config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError("Missing config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_config(base_path, metadata, terrain_data):
        """Writes the config.json file."""
        config_data = {
            "metadata": metadata,
            "settings": {"default_width": 60, "default_height": 40, "cell_size": 20},
            "terrain": terrain_data,
            # Default entity for now
            "entities": [{"type": "player", "id": "player_start", "name": "Player Start", "color": "#FFFFFF", "shape": "star"}]
        }
        
        with open(os.path.join(base_path, "config.json"), 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)