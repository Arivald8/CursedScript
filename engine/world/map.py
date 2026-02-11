import copy

# temp
WALKABLE_CHARS = {'.', '#', ':', ' ', '+', 'T', ','}

class World:
    """
    Container for all game world data, handling terrain map storage 
    and access with bounds checking, entity handling for both items 
    and creatures with coordinate tracking, world population from 
    JSON data using template-based entity instantiation.

    Maintains two parallel tracking systems; list-based storage for iteration
    and dictionary-based coordinate mapping for O(1) spatial queries.
    """
    def __init__(self, width, height, terrain_data):
        self.width = width
        self.height = height
        self.map_data = terrain_data # List of strings from JSON
        
        self.items = []
        self.creatures = []

        self.item_coordinates = {}
        self.creature_coordinates = {}

        self.creature_id_counter = 0

    def load_entities_from_data(self, entity_list, templates):
        """
        Takes the 'entities' list from the map JSON and instantiates objects.
        """
        for ent_data in entity_list:
            x, y = ent_data['x'], ent_data['y']
            e_id = ent_data['id']
            
            # try to find in Creatures
            if e_id in templates['creatures']:
                new_creature = copy.deepcopy(templates['creatures'][e_id])
                self.add_creature(new_creature, x, y)
                
            # try to find in Items
            elif e_id in templates['items']:
                new_item = copy.deepcopy(templates['items'][e_id])
                self.add_item(new_item, x, y)
            
            # special case for Player Start is handled in run_game.py, 
            # but valid to ignore or log.
            elif e_id == "player_start":
                pass
            else:
                print(f"[Warning] Unknown entity ID '{e_id}' at {x},{y}")

    def add_item(self, item, x, y):
        """Places an item at specific coordinates"""
        item.x = x
        item.y = y
        self.items.append(item)
        self.item_coordinates[(y, x)] = item

    def remove_item(self, item):
        """Removes an item (e.g., when picked up)"""
        if item in self.items:
            self.items.remove(item)

        if (item.y, item.x) in self.item_coordinates:
            del self.item_coordinates[(item.y, item.x)]

    def add_creature(self, creature, x, y):
        """Adds a creature to the world and assigns unique dict key"""
        creature.x = x
        creature.y = y 
        self.creature_id_counter += 1
        
        unique_id = f"{creature.name}_{self.creature_id_counter}"

        self.creatures.append(creature)
        self.creature_coordinates[unique_id] = ((y, x), creature)

    def is_valid(self, x, y):
        """Bounds check"""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x, y):
        """Safe way to get a map tile char"""
        if self.is_valid(x, y):
            return self.map_data[y][x]
        return None