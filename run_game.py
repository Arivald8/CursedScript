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
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.noecho()

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    game_path = os.path.join(base_dir, "games", game_folder_name)
    
    if not os.path.exists(game_path):
        stdscr.addstr(0, 0, f"Game not found: {game_path}")
        stdscr.refresh()
        time.sleep(3)
        return

    try:
        loader = GameLoader(game_path)
    except Exception as e:
        stdscr.addstr(0, 0, f"Error loading config: {e}")
        stdscr.refresh()
        time.sleep(3)
        return

    map_file = "level1.json"

    try:
        w, h, terrain, entities = loader.load_map(map_file)
    except FileNotFoundError:
        stdscr.addstr(0, 0, f"Map file '{map_file}' not found in {game_path}/maps/")
        stdscr.refresh()
        time.sleep(3)
        return

    game_world = World(w, h, terrain)
    game_world.load_entities_from_data(entities, loader.templates)

    start_pos = (w // 2, h // 2)
    for ent in entities:
        if ent.get("id") == "player_start":
            start_pos = (ent['x'], ent['y'])
            break

    inv = Inventory(name="Backpack")
    p = Player(name="Hero", inventory=inv)
    
    state = GameState(game_world, player_obj=p)
    state.player_x, state.player_y = start_pos
    
    terrain_config = loader.config.get("terrain", [])
    renderer = GameRenderer(stdscr, terrain_config)

    renderer.init_colors()
    
    input_handler = InputHandler()
    
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