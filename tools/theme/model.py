class ThemeModel:
    """
    Data model for terrain theme definitions, handling storage and manipulation.
    
    Each definition includes character mapping, display symbols, colour codes, 
    and descriptive names. Provides CRUD operations for terrain entries and 
    maintains the data source for theme configs.
    """
    def __init__(self):
        self.terrains = []

    def set_data(self, terrain_list):
        """Load data from external source (config.json)"""
        self.terrains = terrain_list

    def get_data(self):
        """Return current data"""
        return self.terrains

    def add_terrain(self, terrain_dict):
        self.terrains.append(terrain_dict)

    def update_terrain(self, index, terrain_dict):
        if 0 <= index < len(self.terrains):
            self.terrains[index] = terrain_dict

    def delete_terrain(self, index):
        if 0 <= index < len(self.terrains):
            del self.terrains[index]

    def get_terrain(self, index):
        if 0 <= index < len(self.terrains):
            return self.terrains[index]
        return None
    
    def get_default_template(self):
        return {
            "name": "New Terrain",
            "char": "?",
            "symbol": "?",
            "color": "#FFFFFF", # Text color
            "fg": "#000000"     # Background color (based on your engine config)
        }