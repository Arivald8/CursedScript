import curses
from .world.map import WALKABLE_CHARS

class InputHandler:
    # Mapping inventory indices to equipment slot names
    # Index 0-4 are the "Small Sack" (Inventory)
    # Index 5-12 are Equipment slots
    EQ_SLOT_MAP = {
                     5: "head",
        6: "gloves", 7: "torso", 8: "shield",
        9: "weapon", 10: "legs", 11: "spell",
                     12: "boots"
    }

    def handle_input(self, stdscr, state):
        try:
            key = stdscr.getch()
        except curses.error:
            return

        if key == -1:
            return

        # Global quit
        if key in (ord('q'), ord('Q')):
            state.running = False
            return

        # Toggle inventory mode
        if key in (ord('i'), ord('I')):
            self._toggle_inventory(state)
            return

        # Context control
        if state.in_inventory:
            self._handle_inventory_mode(key, state)
        else:
            self._handle_gameplay_mode(key, state)

    def _toggle_inventory(self, state):
        state.in_inventory = not state.in_inventory
        if state.in_inventory:
            state.inv_index = 0
            state.log_message = "Inventory Opened"
        else:
            state.log_message = "Inventory Closed"

    
    # Inventory mode handlers ------------------>
    def _handle_inventory_mode(self, key, state):
        """Input handler for when the inventory screen is open."""

        if key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
            self._navigate_inventory(key, state)
        
        # Actions
        elif key == 10: # Enter Key
            self._action_equip(state)
        elif key in (ord('u'), ord('U')):
            self._action_unequip(state)
        elif key in (ord('d'), ord('D')):
            self._action_drop(state)
        elif key in (ord('x'), ord('X')):
            self._action_destroy(state)

    def _navigate_inventory(self, key, state):
        """Cursor jumping logic between inventory and equipment grids."""

        idx = state.inv_index
        
        if key == curses.KEY_RIGHT:
            if idx < 4 or idx in [6, 7, 9, 10]:
                state.inv_index += 1
        
        elif key == curses.KEY_LEFT:
            if (idx > 0 and idx <= 4) or idx in [7, 8, 10, 11]:
                state.inv_index -= 1

        elif key == curses.KEY_DOWN:
            if idx <= 4: state.inv_index = 7          # Sack -> Torso
            elif idx == 5: state.inv_index = 7        # Head -> Torso
            elif 6 <= idx <= 8: state.inv_index += 3  # Row 2 -> Row 3
            elif 9 <= idx <= 11: state.inv_index = 12 # Row 3 -> Boots

        elif key == curses.KEY_UP:
            if idx == 12: state.inv_index = 10        # Boots -> Legs
            elif 9 <= idx <= 11: state.inv_index -= 3 # Row 3 -> Row 2
            elif 6 <= idx <= 8: state.inv_index = 5   # Row 2 -> Head
            elif idx == 5: state.inv_index = 2        # Head -> Sack Center

    def _action_equip(self, state):
        """Equip item from Sack (indices 0-4)."""

        if state.inv_index > 4:
            state.log_message = "Already equipped."
            return

        inv = state.player_inventory
        if state.inv_index >= len(inv.storage):
            state.log_message = "Empty Slot"
            return

        item_to_equip = inv.storage[state.inv_index]

        if not item_to_equip.slot_type:
            state.log_message = "Cannot equip this."
            return

        # Perform Swap/Equip
        # remove item from inventory list
        inv.remove(state.inv_index)
        
        # call equip on player object
        swapped_item = state.player_obj.equipment.equip(item_to_equip)

        # If there was an item already in that slot, put it back in inventory
        if swapped_item:
            inv.add(swapped_item)
            state.log_message = f"Equipped {item_to_equip.name}, swapped {swapped_item.name}"
        else:
            state.log_message = f"Equipped {item_to_equip.name}"

        # Update stats
        state.player_obj.add_eq_stat(item_to_equip)
        
        state.player_turn_taken = True

    def _action_unequip(self, state):
        """Unequip item from Body (indices 5+)."""

        if state.inv_index < 5:
            state.log_message = "Select an equipped item to unequip."
            return

        slot_name = self.EQ_SLOT_MAP.get(state.inv_index)
        equipped_item = state.player_obj.equipment.slots.get(slot_name)

        if not equipped_item:
            state.log_message = "Slot is empty."
            return

        inv = state.player_inventory
        if len(inv.storage) >= inv.small_sack_cap:
            state.log_message = "Inventory Full!"
            return

        # Perform Unequip
        inv.add(equipped_item)
        state.player_obj.equipment.unequip(slot_name)
        state.player_obj.remove_eq_stat(equipped_item)
        state.log_message = f"Unequipped {equipped_item.name}"

        state.player_turn_taken = True

    def _action_drop(self, state):
        """Drops item from Sack to the floor."""

        if state.inv_index > 4:
            state.log_message = "Unequip first."
            return

        inv = state.player_inventory
        if state.inv_index >= len(inv.storage):
            state.log_message = "Nothing to drop"
            return

        # Check world collision before dropping an item to make sure that cell is empty
        current_pos = (state.player_y, state.player_x)
        if current_pos in state.world.item_coordinates:
            state.log_message = "There is already an item here!"
            return
        
        state.player_turn_taken = True

        item = inv.remove(state.inv_index)
        state.world.add_item(item, state.player_x, state.player_y)
        state.log_message = f"Dropped {item.name}"

    def _action_destroy(self, state):
        """Permanently deletes item from Sack."""

        if state.inv_index > 4:
            state.log_message = "Unequip first."
            return

        inv = state.player_inventory
        if state.inv_index < len(inv.storage):
            item = inv.remove(state.inv_index)
            state.log_message = f"Destroyed {item.name}"
        else:
            state.log_message = "Nothing to destroy"
    # <---------------------------------------------

    # Gameplay mode handlers ---------------------->
    def _handle_gameplay_mode(self, key, state):
        """Handles movement, interaction, and combat."""
        
        # Movement
        if key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
            self._move_player(key, state)
        
        # Actions
        elif key in (ord("e"), ord("E")):
            self._action_pickup(state)
        elif key in (ord("r"), ord("R")):
            self._action_attack(state)

    def _move_player(self, key, state):
        target_x, target_y = state.player_x, state.player_y

        if key == curses.KEY_UP:      target_y -= 1
        elif key == curses.KEY_DOWN:  target_y += 1
        elif key == curses.KEY_LEFT:  target_x -= 1
        elif key == curses.KEY_RIGHT: target_x += 1

        if not state.world.is_valid(target_x, target_y):
            return

        # WALKABLE_CHARS is imported from engine.world.map
        if state.world.get_tile(target_x, target_y) in WALKABLE_CHARS:
            state.player_x = target_x
            state.player_y = target_y
            state.player_turn_taken = True

    def _action_pickup(self, state):
        player_pos = (state.player_y, state.player_x)
        
        # Dictionary lookup (O(1) efficiency)
        item_obj = state.world.item_coordinates.get(player_pos)

        if item_obj:
            if state.player_inventory.add(item_obj):
                state.log_message = f"Picked up {item_obj.name}"
                state.world.remove_item(item_obj)
                state.player_turn_taken = True
            else:
                state.log_message = "Inventory Full!"
        else:
            state.log_message = "Nothing here."

    def _action_attack(self, state):
        p_x, p_y = state.player_x, state.player_y
        atk_range = state.player_obj.attack_range
        hits = 0
        dead_creatures = []
        xp_gained = 0

        # Check all creatures within attack range
        # Note: In a large game, iterating all creatures is slow. 
        # But for this scope, it is acceptable.
        for unique_id, (pos, creature) in state.world.creature_coordinates.items():
            c_y, c_x = pos
            dist_x = abs(p_x - c_x)
            dist_y = abs(p_y - c_y)

            if dist_x <= atk_range and dist_y <= atk_range:
                state.player_obj.attack(creature)
                hits += 1
                if not creature.is_alive():
                    xp_gained += creature.experience
                    dead_creatures.append((unique_id, creature))
        
        # Cleanup dead creatures
        for unique_id, creature_obj in dead_creatures:
            if creature_obj in state.world.creatures:
                state.world.creatures.remove(creature_obj)
            if unique_id in state.world.creature_coordinates:
                del state.world.creature_coordinates[unique_id]

        # Apply xp and check for level up
        leveled_up = False
        if xp_gained > 0:
            leveled_up = state.player_obj.gain_xp(xp_gained)

        if hits > 0:
            if leveled_up:
                state.log_message = f"LEVEL UP! You are now level {state.player_obj.lvl}!"
            elif dead_creatures:
                state.log_message = f"Hit {hits} enemies, killed {len(dead_creatures)}!"
            else:
                state.log_message = f"Attacked {hits} enemies!"
        else:
            state.log_message = "Nothing in range."

        state.player_turn_taken = True