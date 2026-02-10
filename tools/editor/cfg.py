import json
import os

class CFG:
    """
    Configuration file specifically for the editor.

    Contains everything from dimentions, through terrain, entities,
    helper methods and config loading.
    """

    # Fallbacks in case config.json is missing
    DEFAULT_WIDTH = 60
    DEFAULT_HEIGHT = 40
    CELL_SIZE = 20  
    FONT_SIZE = 10

    # Default Terrain Fallback
    TERRAIN_TYPES = [
        {'char': '.', 'color': '#32CD32', 'fg': '#006400', 'name': 'Grass', 'symbol': '·'},
        {'char': ' ', 'color': '#000000', 'fg': '#000000', 'name': 'Void',  'symbol': ''},
    ]

     # Default Entity Fallback
    ENTITY_TYPES = [
        {'type': 'player', 'id': 'player_start', 'name': 'Player Start', 'color': '#FFFFFF', 'shape': 'star'},
    ]

    # Helpers to find data by keys
    @staticmethod
    def get_terrain_by_char(char):
        for t in CFG.TERRAIN_TYPES:
            if t['char'] == char:
                return t
        return CFG.TERRAIN_TYPES[0]
    

    @classmethod
    def update_terrain_data(cls, new_terrain_list):
        """Allows runtime updates of terrain definitions."""
        cls.TERRAIN_TYPES = new_terrain_list


    @classmethod
    def load_config(cls, filename="config.json"):
        """
        Loads configuration from an external JSON file.
        Uses absolute paths to ensure it works regardless of where the script runs.
        """
        # Determine the directory of THIS file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, filename)

        if not os.path.exists(config_path):
            print(f"[WARNING] Config file not found at {config_path}. Using internal defaults.")
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Updating settings
            settings = data.get("settings", {})
            cls.DEFAULT_WIDTH = settings.get("default_width", cls.DEFAULT_WIDTH)
            cls.DEFAULT_HEIGHT = settings.get("default_height", cls.DEFAULT_HEIGHT)
            cls.CELL_SIZE = settings.get("cell_size", cls.CELL_SIZE)
            cls.FONT_SIZE = settings.get("font_size", cls.FONT_SIZE)

            # Updating terrain (if present and valid)
            if "terrain" in data and isinstance(data["terrain"], list):
                cls.TERRAIN_TYPES = data["terrain"]

            # Updating entities (if present and valid)
            if "entities" in data and isinstance(data["entities"], list):
                cls.ENTITY_TYPES = data["entities"]
                
            print(f"[INFO] Configuration loaded from {config_path}")

        except Exception as e:
            print(f"[ERROR] Failed to parse config.json: {e}")
            print("Reverting to internal defaults.")

CFG.load_config()