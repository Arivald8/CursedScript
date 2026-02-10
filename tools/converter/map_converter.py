"""
Just a convenience tool to allow for creative map design.
Converts any PNG image to JSON map format for CursedScript.

Transforms pixels into ASCII-based terrain representations with
colour classification, preserving both terrain layout and entity placements. 

Also supports legacy entity migration from previous JSON files while 
generating new unified map files compatible with the current engine.

:
    Color-to-ASCII classification using HSV color space analysis
    Aspect ratio correction for terminal character proportions (0.55 height multiplier)
    Legacy entity preservation and migration
    Configurable output dimensions and target width
"""

import json
import os
import colorsys
from PIL import Image

INPUT_IMAGE_PATH: str = 'map_template.png' 

# Optionally can accept an old JSON file containing entities.
# This has been superseeded by new JSON file saves, but left 
# here for backward compatibility. Set to None if not needed.
INPUT_ENTITIES_JSON: str | None = None

# The name of the file to generate for the new engine implementation
OUTPUT_JSON_PATH: str = 'level1.json'

# How wide the map SHOULD be (Height is calculated automatically)
TARGET_WIDTH = 100

# ==========================================
# COLOR MAPPING GUIDE:
# ------------------------------------------
# BLACK        -> ' ' (Void)
# DARK GREY    -> 'M' (Cave/Rock)
# GREY         -> 'x' (Stone Wall)
# WHITE        -> '^' (Mountain)
# CYAN/PALE    -> '_' (Ice)
# BLUE         -> '~' (Water)
# DARK GREEN   -> 'T' (Tree/Forest)
# BRIGHT GREEN -> ',' (Tall Grass)
# STD GREEN    -> '.' (Grass)
# YELLOW       -> ':' (Sand)
# BRIGHT GOLD  -> '$' (Gold/Treasure)
# LIGHT BROWN  -> '#' (Road)
# DARK BROWN   -> '=' (Bridge/Wood)
# RED          -> 'O' (Building)
# PURPLE/PINK  -> '!' (Potion)
# ORANGE       -> '+' (Door)
# ==========================================

def rgb_to_hsv(r, g, b):
    return colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

def classify_terrain(pixel_rgb):
    r, g, b = pixel_rgb
    h, s, v = rgb_to_hsv(r, g, b)

    # Achromatic (Greys, Blacks, Whites) -->
    # Void (Pure Black)
    if v < 0.1:
        return ' ' 
    # Cave / Dark Rock (Very Dark Grey)
    if v < 0.25:
        return 'M'
    # Low Saturation areas (Greys, Whites)
    if s < 0.15:
        # Mountain (White/Bright Grey)
        if v > 0.75:
            return '^'
        # Stone Wall (Medium Grey)
        return 'x'


    # Blues (Water, Ice) 
    if 0.46 <= h <= 0.68:
        # Ice / Fog (High Brightness, Lower Saturation Cyan/Blue)
        if v > 0.8 and s < 0.4:
            return '_'
        # Standard Water
        return '~'

    # Greens (Nature)
    if 0.20 <= h <= 0.45:
        # Deep Forest (Dark Green)
        if v < 0.40:
            return 'T'
        # Tall Grass / Bush (High Saturation/Neon Green)
        if s > 0.8:
            return ','
        # Small Tree / Bush alternative (Blue-ish Green)
        if h > 0.40:
             return 't'
        # Standard Grass
        return '.'


    # Yellows/Browns (Earth, Wood, Gold)
    if 0.07 <= h <= 0.18:
        # Gold / Treasure (Very Bright, High Saturation Yellow)
        if v > 0.9 and s > 0.8:
            return '$'
        # Sand (High Brightness, Medium Saturation)
        if v > 0.70:
            return ':'
        # Wood / Bridge (Dark Brown)
        if v < 0.45:
            return '='
        # Road / Path (Standard Tan/Brown)
        return '#'

    # Reds (Buildings, Blood, Fire)
    # Hue wraps around 0 and 1
    if h < 0.07 or h > 0.93:
        # Dragon or Danger (Very Bright Red)
        if v > 0.9 and s > 0.9:
            return 'D' 
        # Building / Roof (Standard Red)
        return 'O'

    # Oranges (Doors, Copper)
        # Door (Orange)
        return '+'

    # Purples/Magentas (Magic, Items)
    if 0.75 <= h <= 0.93:
        # Potion (Pink/Magenta)
        if s > 0.5:
            return '!'
        # Scroll (Pale Purple)
        return '?'

    # Fallback if a color is weird, assume it's generic floor
    return '.'

def load_entities(json_path):
    """Loads the old entity list if the file exists."""
    if not json_path or not os.path.exists(json_path):
        return []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Loaded {len(data)} entities from {json_path}")
            return data
    except Exception as e:
        print(f"Error loading entities: {e}")
        return []

def convert_map():
    if not os.path.exists(INPUT_IMAGE_PATH):
        print(f"Error: {INPUT_IMAGE_PATH} not found.")
        return

    try:
        img = Image.open(INPUT_IMAGE_PATH)
    except Exception as e:
        print(f"Error opening image {INPUT_IMAGE_PATH}: {e}")
        return

    width, height = img.size
    aspect_ratio = height / width
    # 0.55 aspect ratio correction because terminal characters are taller than they are wide
    new_height = int(aspect_ratio * TARGET_WIDTH * 0.55)
    
    print(f"Resizing image to {TARGET_WIDTH}x{new_height}...")
    
    # NEAREST is important to keep hard edges on pixel art
    img = img.resize((TARGET_WIDTH, new_height), Image.Resampling.NEAREST)
    img = img.convert('RGB')
    pixels = img.load()

    terrain_rows = []
    
    print("Classifying pixels...")
    for y in range(new_height):
        row_str = ""
        for x in range(TARGET_WIDTH):
            pixel = pixels[x, y]
            char = classify_terrain(pixel)
            row_str += char
        terrain_rows.append(row_str)

    entities = load_entities(INPUT_ENTITIES_JSON)

    unified_data = {
        "dimensions": {
            "width": TARGET_WIDTH,
            "height": new_height
        },
        "terrain": terrain_rows,
        "entities": entities
    }

    try:
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, indent=4)
        print(f"Success! Unified map saved to: {OUTPUT_JSON_PATH}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

if __name__ == "__main__":
    convert_map()