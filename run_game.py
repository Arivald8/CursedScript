import curses
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'engine'))

from engine.loader import GameLoader
from engine.world.map import World
from engine.state import GameState
from engine.renderer import GameRenderer
from engine.input import InputHandler
from engine.world.objects import Player, Inventory

FPS = 60
FRAME_TIME = 1 / FPS

def game_loop(stdscr, game_folder_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    game_path = os.path.join(base_dir, "games", game_folder_name)
    
    if not os.path.exists(game_path):
        print(f"Game not found: {game_folder_name}")
        return

    loader = GameLoader(game_path)

    # Loading map (Assuming a starting map defined in config)
    w, h, terrain, entities = loader.load_map("level1.json")

    game_world = World(w, h, terrain)
    game_world.load_entities_from_data(entities, loader.templates)

    player_start = (w//2, h//2)
    # Searching entity list for player_start id
    for e in entities:
        if e.get('id') == 'player_start':
            player_start = (e['x'], e['y'])

    inv = Inventory(name="Backpack")
    p = Player(name="Hero", inventory=inv)
    
    state = GameState(game_world, player_obj=p)
    state.player_x, state.player_y = player_start
    
    renderer = GameRenderer(stdscr)
    input_handler = InputHandler()
    
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.noecho()

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1) # Grass, etc...

    last_time = time.perf_counter()

    while state.running:
        current_time = time.perf_counter()
    
        input_handler.handle_input(stdscr, state)
    
        renderer.render(state, p, current_time)

        time.sleep(FRAME_TIME)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_game.py <game_folder_name>")
        print("Example: python run_game.py sample_quest")
    else:
        curses.wrapper(game_loop, sys.argv[1])