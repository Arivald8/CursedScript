class CFG:
    # CONF
    DEFAULT_WIDTH = 60
    DEFAULT_HEIGHT = 40
    CELL_SIZE = 20  
    FONT_SIZE = 10

    # Helpers to find data by keys
    @staticmethod
    def get_terrain_by_char(char):
        for t in CFG.TERRAIN_TYPES:
            if t['char'] == char:
                return t
        return CFG.TERRAIN_TYPES[0]

    TERRAIN_TYPES = [
        {'char': '.', 'color': '#32CD32', 'fg': '#006400', 'name': 'Grass',     'symbol': '·'},
        {'char': 'T', 'color': '#228B22', 'fg': '#000000', 'name': 'Tree',      'symbol': '♠'},
        {'char': '~', 'color': '#1E90FF', 'fg': '#E0FFFF', 'name': 'Water',     'symbol': '≈'},
        {'char': '#', 'color': '#DAA520', 'fg': '#8B4513', 'name': 'Road',      'symbol': '░'},
        {'char': ':', 'color': '#F0E68C', 'fg': '#BDB76B', 'name': 'Sand',      'symbol': '░'},
        {'char': '^', 'color': '#D3D3D3', 'fg': '#000000', 'name': 'Mountain',  'symbol': '▲'},
        {'char': 'x', 'color': '#696969', 'fg': '#D3D3D3', 'name': 'Wall',      'symbol': '▒'},
        {'char': 'M', 'color': '#2F4F4F', 'fg': '#708090', 'name': 'Cave/Rock', 'symbol': '█'},
        {'char': 'O', 'color': '#8B0000', 'fg': '#FFFFFF', 'name': 'Building',  'symbol': '⌂'},
        {'char': '+', 'color': '#4682B4', 'fg': '#FFD700', 'name': 'Bridge',    'symbol': '≡'},
        {'char': ' ', 'color': '#000000', 'fg': '#000000', 'name': 'Void',      'symbol': ''},
    ]

    # (Saved to JSON)
    ENTITY_TYPES = [
        {'type': 'player',   'id': 'player_start', 'name': 'Player Start', 'color': '#FFFFFF', 'shape': 'star'},
        {'type': 'creature', 'id': 'Ogre',         'name': 'Ogre',         'color': '#FF0000', 'shape': 'oval'},
        {'type': 'creature', 'id': 'Goblin',       'name': 'Goblin',       'color': '#FF69B4', 'shape': 'oval'},
        {'type': 'item',     'id': 'Sword',        'name': 'Sword',        'color': '#00FFFF', 'shape': 'diamond'},
        {'type': 'item',     'id': 'Potion',       'name': 'Health Pot',   'color': '#00FF00', 'shape': 'diamond'},
        {'type': 'item',     'id': 'Shield',       'name': 'Shield',       'color': '#FFA500', 'shape': 'diamond'},
    ]