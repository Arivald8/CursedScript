from .world.objects import Inventory

class GameState:
    def __init__(self, world_obj, player_obj):
        self.world = world_obj
        self.player_obj = player_obj

        self.running = True
        
        self.player_x = self.world.width // 2
        self.player_y = self.world.height // 2
        
        self.in_inventory = False 
        self.inv_index = 0        
        self.log_message = "" 

        self.player_turn_taken = False

        self.player_inventory = player_obj.inventory