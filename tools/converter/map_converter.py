import json
import os
import colorsys
from PIL import Image

INPUT_IMAGE_PATH: str = 'map_template.png' 

# Optionally the old JSON file (from nitem) containing entities (Ogres, Player, etc.)
# Set to None if not needed or want a blank entity list.
INPUT_ENTITIES_JSON: str | None = None

# The name of the file to generate for the new engine
OUTPUT_JSON_PATH: str = 'level1.json'

# How wide the map should be (Height is calculated automatically)
TARGET_WIDTH = 150 
# ==========================================

def rgb_to_hsv(r, g, b):
    return colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

def classify_terrain(pixel_rgb):
    r, g, b = pixel_rgb
    h, s, v = rgb_to_hsv(r, g, b)

    # Water (Blue/Cyan)
    if 0.45 <= h <= 0.68 and v > 0.20:
        if v < 0.35: return '~' # Deep water
        return '~'

    # Buildings (Red/Orange Roofs)
    is_red_hue = (h < 0.05 or h > 0.94)
    if is_red_hue and s > 0.35 and v > 0.30:
        return 'O'

    # Stone walls (Dark Grey)
    if s < 0.15 and 0.20 <= v <= 0.50:
        return 'x'

    # Bridges / WOOD (Dark Brown)
    if 0.05 <= h <= 0.14 and s > 0.30 and 0.20 <= v <= 0.45:
        return '+'

    # Sand
    if 0.08 <= h <= 0.17 and v > 0.65 and s < 0.5:
        return ':'

    # Read
    if 0.05 <= h <= 0.16 and 0.45 < v <= 0.70:
        return '#'

    # Mountain (Bright Grey/White)
    if s < 0.15 and v > 0.50:
        return '^'

    # Forest (Dark Green)
    if 0.20 <= h <= 0.40 and v < 0.40:
        return 'T'

    # Grass (General Green)
    if 0.18 <= h <= 0.45:
        return '.'

    # Caves
    if v < 0.20:
        return 'M'

    # Fallback
    return '.'

def load_entities(json_path):
    """Loads the old entity list if the file exists."""
    if not json_path or not os.path.exists(json_path):
        print(f"No entity file found at {json_path}, starting with empty entities.")
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
    try:
        img = Image.open(INPUT_IMAGE_PATH)
    except Exception as e:
        print(f"Error opening image {INPUT_IMAGE_PATH}: {e}")
        return

    width, height = img.size
    aspect_ratio = height / width
    # 0.55 aspect ratio correction for terminal characters
    new_height = int(aspect_ratio * TARGET_WIDTH * 0.55)
    
    print(f"Resizing image to {TARGET_WIDTH}x{new_height}...")
    
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