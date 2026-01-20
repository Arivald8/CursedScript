# Dev note: New loader not present in nitem

import json
import os
from .world.objects import Item, Creature

class GameLoader:
    def __init__(self, game_dir):
        self.game_dir = game_dir
        self.config = self.load_config()
        self.templates = self.parse_templates()

    def load_config(self):
        """Loads the main game conf (item defs, settings)."""
        path = os.path.join(self.game_dir, "config.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config not found at {path}")
            
        with open(path, 'r') as f:
            return json.load(f)
        
    def parse_templates(self):
        """
        Parses the 'entities' list from config.json into reusable objects.
        """
        templates = {'items': {}, 'creatures': {}}
        
        raw_entities = self.config.get("entities", [])
        
        for ent_def in raw_entities:
            e_id = ent_def.get("id")
            e_type = ent_def.get("type")
            
            # Map JSON keys to Class __init__ arguments
            # We pass the whole dict as kwargs. 
            # The Classes use **kwargs to accept extra visual data (like "color") safely.
            
            if e_type == "creature":
                # defaults for stats if missing in JSON
                defaults = {
                    "hp": 10, "strength": 1, "defense": 0, "icon": "?"
                }
                # defaults with definition
                data = {**defaults, **ent_def}
                # blueprint instance
                templates['creatures'][e_id] = Creature(**data)
                
            elif e_type == "item":
                defaults = {
                    "attack": 0, "slot_type": None, "icon": "?"
                }
                data = {**defaults, **ent_def}
                templates['items'][e_id] = Item(**data)
                
        return templates
    
    def load_map(self, map_filename):
        """
        Loads unified JSON map format.
        """
        path = os.path.join(self.game_dir, "maps", map_filename)
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        width = data['dimensions']['width']
        height = data['dimensions']['height']
        terrain = data['terrain'] 
        entities = data.get('entities', [])

        return width, height, terrain, entities
        