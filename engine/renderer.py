import curses

class GameRenderer:
    """
    Main renderer handling terminal display of game elements.

    Manages all curses-based rendering operations for terminal game config. 
    
    It handles:
    - Terrain rendering with configurable ASCII symbols and colors
    - Camera/viewport management for scrolling worlds
    - Entity and object rendering (player, items, creatures)
    - UI components (inventory, stats, controls)
    - Colour palette initialization from hex/RGB values

    The renderer uses a config-driven approach where terrain appearance is defined
    in JSON configuration files, allowing for theme customization.
    """


    def __init__(self, stdscr, terrain_config=None):
        self.stdscr = stdscr
        self.sh, self.sw = stdscr.getmaxyx()
        
        self.terrain_config = terrain_config if terrain_config else []
        self.char_map = {} # Cache for char -> (render_char, color_pair_id)

        self.cam_x = 0
        self.cam_y = 0
        self.ui_height = 2
        self.inv_width = 0

    def _hex_to_curses_color(self, hex_code):
        """
        Approximates a HEX string (e.g., '#32CD32') to a curses color constant.
        Returns: (curses_color_const, is_bold)
        """
        if not hex_code or not isinstance(hex_code, str):
            return curses.COLOR_BLACK, False 
            
        hex_code = hex_code.lstrip('#')
        try:
            r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return curses.COLOR_WHITE, False

        # Determine boldness (brightness)
        # If the max channel is very high, we treat it as bold (bright)
        m = max(r, g, b)
        is_bold = m > 160 

        # find nearest standard color
        # Grayscale checks
        if r < 50 and g < 50 and b < 50: return curses.COLOR_BLACK, False
        if r > 150 and g > 150 and b > 150: return curses.COLOR_WHITE, is_bold
        if abs(r-g) < 30 and abs(g-b) < 30 and abs(r-b) < 30: 
            # Greyish, map to black(bold) or white(dim) depending on intensity
            return curses.COLOR_BLACK if m < 128 else curses.COLOR_WHITE, True

        # Colour dominance
        if r > g and r > b:
            if g > r * 0.6: return curses.COLOR_YELLOW, is_bold
            if b > r * 0.6: return curses.COLOR_MAGENTA, is_bold
            return curses.COLOR_RED, is_bold
            
        if g > r and g > b:
            if r > g * 0.6: return curses.COLOR_YELLOW, is_bold
            if b > g * 0.6: return curses.COLOR_CYAN, is_bold
            return curses.COLOR_GREEN, is_bold
            
        if b > r and b > g:
            if r > b * 0.6: return curses.COLOR_MAGENTA, is_bold
            if g > b * 0.6: return curses.COLOR_CYAN, is_bold
            return curses.COLOR_BLUE, is_bold
        
        return curses.COLOR_WHITE, is_bold

    def init_colors(self):
        """
        Initializes curses colors based on the loaded configuration.
        """
        if not curses.has_colors():
            return

        curses.start_color()
        curses.use_default_colors()

        #  basic pairs (ID 1-9 reserved for UI/Actors)
        curses.init_pair(1, curses.COLOR_WHITE, -1)   # Default UI
        curses.init_pair(2, curses.COLOR_RED, -1)     # Enemies
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Items
        curses.init_pair(4, curses.COLOR_CYAN, -1)    # Player
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE) # UI Highlight
        curses.init_pair(11, curses.COLOR_WHITE, -1)  # Inventory Text
        curses.init_pair(12, curses.COLOR_YELLOW, -1) # Selection
        curses.init_pair(13, curses.COLOR_RED, -1)    # Creature default

        # Dynamic terrain colors (IDs 10+)
        # Need to map the JSON definition to Curses pairs.
        # Since JSON has hex/names, using a simplified mapping for this.
        
        pair_id = 20
        for t_def in self.terrain_config:
            char = t_def['char']
            symbol = t_def.get('symbol', char)
            if not symbol: 
                symbol = char

            # Fix for TypError ensuring symbol is exactly 1 char long for addch
            if len(symbol) > 1:
                symbol = symbol[0]

            fg_hex = t_def.get('color', '#FFFFFF') 
            bg_hex = t_def.get('fg', None) 
            
            # Resolve curses colors
            fg_const, fg_bold = self._hex_to_curses_color(fg_hex)
            
            bg_const = -1
            if bg_hex:
                 # Backgrounds in standard curses (init_pair) cannot be bold, 
                 # so we ignore the bold return value for BG
                bg_const, _ = self._hex_to_curses_color(bg_hex)

            try:
                curses.init_pair(pair_id, fg_const, bg_const)
            except Exception:
                # Fallback if too many pairs or error
                pass
            
            attr = curses.color_pair(pair_id)
            if fg_bold:
                attr = attr | curses.A_BOLD

            self.char_map[char] = (symbol, attr)
            pair_id += 1

    def update_dimensions(self):
        """Handle terminal resizing"""
        self.sh, self.sw = self.stdscr.getmaxyx()

    def update_camera(self, target_x, target_y):
        """Centers the camera on the target (player)"""
        self.cam_x = target_x - (self.sw // 2)
        self.cam_y = target_y - (self.sh // 2)

    def world_to_screen(self, w_x, w_y):
        """
        Converts world coordinates to screen coordinates.
        Returns (s_x, s_y) or None if off-screen.
        """
        s_x = w_x - self.cam_x
        s_y = w_y - self.cam_y

        # Check bounds:
        # Width: must be positive and less than screen width minus inventory sidebar
        # Height: must be positive and less than screen height minus bottom UI
        if 0 <= s_x < (self.sw - self.inv_width) and 0 <= s_y < (self.sh - self.ui_height):
            return s_x, s_y
        return None

    def get_tile_render_data(self, char):
        """Looks up character in the config-generated map."""
        if char in self.char_map:
            return self.char_map[char]
        
        # Fallback if map file contains a char not in config
        return char, curses.color_pair(1)

    def draw_text_anchored(self, text, anchor="top_left", offset_x=0, offset_y=0, color=0):
        """
        Draws text relative to a specific anchor point. 
        Anchors: "top_left", "top_right", "bottom_left", "bottom_right", "center"
        """
        y = 0
        x = 0

        if "top" in anchor:
            y = offset_y
        elif "bottom" in anchor:
            y = self.sh - 1 - offset_y
        elif "center" in anchor:
            y = (self.sh // 2) + offset_y
        
        if "left" in anchor:
            x = offset_x
        elif "right" in anchor:
            x = self.sw - len(text) - offset_x
        elif "center" in anchor:
            x = (self.sw // 2) - (len(text) // 2) + offset_x

        if 0 <= y < self.sh and 0 <= x < self.sw:
            try:
                self.stdscr.addstr(y, x, text, color)
            except curses.error as e:
                print(e)

    def _draw_map(self, state):
        # Iterate only over the screen area, not the whole map
        view_h = self.sh - self.ui_height
        view_w = self.sw - self.inv_width

        for y in range(view_h):
            for x in range(view_w):
                map_x = self.cam_x + x
                map_y = self.cam_y + y

                if state.world.is_valid(map_x, map_y):
                    logic_char = state.world.map_data[map_y][map_x]
                    char, color = self.get_tile_render_data(logic_char)
                    try:
                        self.stdscr.addch(y, x, char, color)
                    except curses.error:
                        pass

    def _draw_player(self, state, blink_state):
        pos = self.world_to_screen(state.player_x, state.player_y)
        if pos:
            item_at_feet = any(i.x == state.player_x and i.y == state.player_y for i in state.world.items)
            if item_at_feet and not blink_state: return

            self.stdscr.addch(pos[1], pos[0], '@', curses.color_pair(4) | curses.A_BOLD)

            # if standing on item, and blink is off, skip drawing player
            if item_at_feet and not blink_state:
                return

            self.stdscr.addch(pos[1], pos[0], '@', curses.color_pair(5) | curses.A_BOLD)

    def _draw_items(self, state):
        for item in state.world.items:
            pos = self.world_to_screen(item.x, item.y)
            if pos:
                try:
                    self.stdscr.addch(pos[1], pos[0], item.icon, curses.color_pair(3) | curses.A_BOLD)
                except curses.error as e:
                    print(e)

    def _draw_creatures(self, state, blink_state):
        for creature in state.world.creatures:
            pos = self.world_to_screen(creature.x, creature.y)
            if pos:
                # blink logic: creature vs player
                if creature.x == state.player_x and creature.y == state.player_y:
                    # if blink is on, skip drawing creature
                    if blink_state:
                        continue
                try:
                    self.stdscr.addch(pos[1], pos[0], creature.icon, curses.color_pair(13))
                except curses.error as e:
                    print(e)


    def _draw_inventory(self, state, player_obj):
        inv_lines = player_obj.inventory.get_ui_lines()
        self.inv_width = max(len(line) for line in inv_lines) + 1 if inv_lines else 0
        base_x = self.sw - 23 # approx width of UI box

        for idx, line in enumerate(inv_lines):
            draw_x = self.sw - len(line)
            draw_y = idx
            try:
                self.stdscr.addstr(draw_y, draw_x, line, curses.color_pair(11))
            except curses.error as e:
                print(e)

        # draw inventory sack items
        sack_y = 2 # sack is on line index 2
        sack_base_x = self.sw - len(inv_lines[sack_y])
        SLOT_START_INDEX = 2
        SLOT_WIDTH = 4

        try:
            for i, item in enumerate(player_obj.inventory.storage):
                item_offset = SLOT_START_INDEX + (i * SLOT_WIDTH) + 1
                self.stdscr.addch(sack_y, sack_base_x + item_offset, item.icon, curses.A_BOLD)
            
            if state.in_inventory and state.inv_index < 5:
                cursor_offset = SLOT_START_INDEX + (state.inv_index * SLOT_WIDTH)
                self.stdscr.addch(sack_y, sack_base_x + cursor_offset, '[', curses.color_pair(12) | curses.A_BOLD)
                self.stdscr.addch(sack_y, sack_base_x + cursor_offset + 2, ']', curses.color_pair(12) | curses.A_BOLD)
        except curses.error as e:
            print(e)

        # We map slot names to (Line_Index, Char_Index_Offset_From_Right)
        # Based on:
        # 5: "          [ ]          " (Head) -> Center is approx 11 chars in
        # 6: "      [ ] [ ] [ ]      " (Gloves, Torso, Shield)
        # 7: "      [ ] [ ] [ ]      " (Weapon, Legs, Spell)
        # 8: "          [ ]          " (Boots)
        
        # Note: offsets are approximate based on the string lengths in inventory.py
        # Width of UI is 23 chars. 
        # Center [ ] is at index 10,11,12 (bracket, space, bracket) -> Icon at 11

        eq_coords = {
            "head":   (5, 11),
            "gloves": (6, 7),
            "torso":  (6, 11),
            "shield": (6, 15),
            "weapon": (7, 7),
            "legs":   (7, 11),
            "spell":  (7, 15),
            "boots":  (8, 11)
        }

        index_to_slot = {
            5: "head",
            6: "gloves",
            7: "torso",
            8: "shield",
            9: "weapon",
            10: "legs",
            11: "spell",
            12: "boots"
        }

        # draw icons
        for slot_name, item in player_obj.equipment.slots.items():
            if item and slot_name in eq_coords:
                line_idx, char_offset = eq_coords[slot_name]
                try:
                    self.stdscr.addch(line_idx, base_x + char_offset, item.icon, curses.A_BOLD)
                except curses.error:
                    pass

        # draw cursor if in equipment (5-12)
        if state.in_inventory and state.inv_index >= 5:
            current_slot_name = index_to_slot.get(state.inv_index)
            if current_slot_name and current_slot_name in eq_coords:
                line_idx, char_offset = eq_coords[current_slot_name]
                try:
                    # draw bracked around speficif slot
                    self.stdscr.addch(line_idx, base_x + char_offset - 1, '[', curses.color_pair(12) | curses.A_BOLD)
                    self.stdscr.addch(line_idx, base_x + char_offset + 1, ']', curses.color_pair(12) | curses.A_BOLD)
                except curses.error:
                    pass


    def _draw_stats(
        self, player_obj):
        hp_str =   f"{player_obj.hp}/{player_obj.max_hp}"
        str_str =  f"{player_obj.strength}"
        range_str = f"{player_obj.attack_range}"
        def_str =  f"{player_obj.defense}"
        mana_str = f"{player_obj.mana}"
        lvl_str = f"{player_obj.lvl}"
        xp_str = f"{player_obj.experience}"

        style = curses.color_pair(3) | curses.A_BOLD

        # Offset Y: 11 (Inventory is roughly 10 lines tall)
        # Offset X: 2 (small padding from the right edge)
        self.draw_text_anchored("HP:", anchor="bottom_right", offset_x=11, offset_y=1, color=style)
        self.draw_text_anchored(hp_str, anchor="bottom_right", offset_x=0, offset_y=1, color=style)

        self.draw_text_anchored("MANA:", anchor="bottom_right", offset_x=9, offset_y=2, color=style)
        self.draw_text_anchored(mana_str, anchor="bottom_right", offset_x=0, offset_y=2, color=style)

        self.draw_text_anchored("STR:", anchor="bottom_right", offset_x=10, offset_y=3, color=style)
        self.draw_text_anchored(str_str, anchor="bottom_right", offset_x=0, offset_y=3, color=style)

        self.draw_text_anchored("DEF:", anchor="bottom_right", offset_x=10, offset_y=4, color=style)
        self.draw_text_anchored(def_str, anchor="bottom_right", offset_x=0, offset_y=4, color=style)
        
        self.draw_text_anchored("RANGE:", anchor="bottom_right", offset_x=8, offset_y=5, color=style)
        self.draw_text_anchored(range_str, anchor="bottom_right", offset_x=0, offset_y=5, color=style)

        self.draw_text_anchored("LVL:", anchor="bottom_right", offset_x=10, offset_y=6, color=style)
        self.draw_text_anchored(lvl_str, anchor="bottom_right", offset_x=0, offset_y=6, color=style)

        self.draw_text_anchored("XP:", anchor="bottom_right", offset_x=11, offset_y=7, color=style)
        self.draw_text_anchored(xp_str, anchor="bottom_right", offset_x=0, offset_y=7, color=style)
    

    def _draw_ui(self, state, player_name):
        try:
            # Bottom UI Y position
            ui_y = self.sh - 2

            # Log / Coords
            if state.log_message:
                msg = f" {state.log_message} "
                self.stdscr.addstr(ui_y, 0, msg, curses.color_pair(12)) 
            else:
                coords = f" X:{state.player_x} Y:{state.player_y} "
                self.stdscr.addstr(ui_y, 0, coords, curses.color_pair(3) | curses.A_REVERSE)

            # Controls
            if state.in_inventory:
                controls = "[Arrows]:Move [Ent]:Equip [U]:Unequip [D]:Drop [X]:Destr"
            else:
                controls = "[I]:Inv  [Q]:Quit  [E]:Pick Up  [Arrows]:Move"
                
            self.stdscr.addstr(ui_y, 30, controls, curses.color_pair(3))
            self.stdscr.addstr(ui_y + 1, 0, player_name)

        except curses.error as e:
            print(e)

    def render(self, state, player_obj, current_time):
        """
        Main public method to draw everything.
        """
        self.stdscr.erase()

        self.update_dimensions() # Check for resize
        self.update_camera(state.player_x, state.player_y)

        # blink state
        # 3 blinks per second approx
        blink_state = int(current_time * 3) % 2 == 0

        #(Calculation of inv_width happens here)
        self._draw_inventory(state, player_obj)

        #(Uses inv_width calculated above)
        self._draw_map(state)

        self._draw_items(state)
        self._draw_player(state, blink_state)
        self._draw_creatures(state, blink_state)
        self._draw_ui(state, player_obj.name)
        self._draw_stats(player_obj)

        self.stdscr.refresh()