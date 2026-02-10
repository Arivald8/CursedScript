class Entity:
    """
    Base class for all game objects with position, visual representation, and name.
    """
    def __init__(self, x=0, y=0, name="Unknown", icon="?", color_pair=0, **kwargs):
        self.x = x
        self.y = y
        self.name = name
        self.icon = icon
        self.color_pair = color_pair


class Item(Entity):
    """
    Extends Entity, representing collectible objects with combat stats and equipment slots.
    """
    def __init__(self, name, type, icon, attack=0, slot_type=None, **kwargs):
        super().__init__(name=name, icon=icon, **kwargs)
        self.type = type
        self.attack = attack
        self.slot_type = slot_type

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class Creature(Entity):
    """
    Extends Entity, representing living entities with health, combat stats, and behaviours.
    """
    def __init__(self,
            name, 
            hp, 
            strength, 
            defense,
            icon,
            experience=0,
            attack_range=1,
            attack_speed=2.0,
            **kwargs
        ):
        super().__init__(name=name, icon=icon, **kwargs)

        self.hp = hp
        self.max_hp = hp
        self.strength = strength
        self.defense = defense
        self.experience = experience
        self.attack_range = attack_range
        self.attack_speed = attack_speed
        self.last_attack_time = 0.0

    def is_alive(self):
        return self.hp > 0
    
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def attack(self, target):
        damage = self.strength - target.defense
        if damage < 0:
            damage = 0
        target.take_damage(damage)
        return damage


class Equipment:
    """
    Manages equipped items across eight gear slots with swap/unequip functionality.
    """
    def __init__(self):
        self.slots = {
            "head": None,
            "torso": None,
            "gloves": None,
            "legs": None,
            "boots": None,
            "weapon": None,
            "shield": None,
            "spell": None
        }

    def equip(self, item):
        """
        Returns the item that was previously equipped (to swap), or None.
        """
        if not item.slot_type or item.slot_type not in self.slots:
            return item # Cannot equip, return the item back
        
        previous = self.slots[item.slot_type]
        self.slots[item.slot_type] = item
        return previous
    
    def unequip(self, slot_type):
        if slot_type in self.slots:
            item = self.slots[slot_type]
            self.slots[slot_type] = None
            return item
        return None


class Inventory:
    """
    Container for items with limited capacity and UI representation generation.
    """
    def __init__(self, name):
        self.name = name
        self.storage = []
        self.small_sack_cap = 5

    def add(self, item):
        if len(self.storage) < self.small_sack_cap:
            self.storage.append(item)
            return True
        else:
            return False
        
    def remove(self, index):
        if 0 <= index < len(self.storage):
            return self.storage.pop(index)
        return None
    
    def get_ui_lines(self):
        return [
            "        INVENTORY      ",
            "-----------------------",
            "| [ ] [ ] [ ] [ ] [ ] |", # Line 2: Inventory Slots
            "-----------------------",
            "       EQUIPMENT       ",
            "          [ ]          ", # Line 5: Head
            "      [ ] [ ] [ ]      ", # Line 6: Gloves, Torso, Shield
            "      [ ] [ ] [ ]      ", # Line 7: Weapon, Legs, Spell
            "          [ ]          ", # Line 8: Boots
            "                       "
        ]
        

class Player(Creature):
    """
    Extends Creature, representing the player character with level progression, inventory, and equipment systems.
    """
    experience_dict = {
        0: 1,
        100: 2,
        500: 3,
        1000: 4,
        2000: 5,
        4000: 6
    }

    GROWTH_HP = 10
    GROWTH_STR = 1
    GROWTH_DEF = 1
    GROWTH_MANA = 5

    def __init__(self, name, inventory=None):
        super().__init__(name=name, hp=100, strength=10, defense=1, icon="@")

        self.inventory = inventory or Inventory("Backpack")
        self.equipment = Equipment()
        self.mana = 100
        self.eq_stats = {} # {"weapon": (10, 10), "..."} = (attack, attack_range)

    @property
    def lvl(self):
        current_lvl = 1
        thresholds = sorted(self.experience_dict.items())

        for xp_req, level_val in thresholds:
            if self.experience >= xp_req:
                current_lvl = level_val
            else:
                break
        return current_lvl
    
    def gain_xp(self, amount):
        # Returns True if a level up occured
        old_level = self.lvl
        self.experience += amount
        if self.lvl > old_level:
            self._apply_level_up(self.lvl - old_level)
            return True
        return False
    
    def _apply_level_up(self, levels_gained):
        self.max_hp += (self.GROWTH_HP * levels_gained)
        self.strength += (self.GROWTH_STR * levels_gained)
        self.defense += (self.GROWTH_DEF * levels_gained)
        self.mana += (self.GROWTH_MANA * levels_gained)

        # Full heal on level up
        self.hp = self.max_hp
            
    def add_eq_stat(self, item):
        for k, v in self.equipment.slots.items():
            if v is not None:
                self.eq_stats[k] = (v.attack, v.attack_range)
        
        if item.slot_type == "weapon":
            self.strength += self.eq_stats["weapon"][0]
            self.attack_range += self.eq_stats["weapon"][1]

    def remove_eq_stat(self, item):
        if item.slot_type == "weapon":
            self.strength -= self.eq_stats["weapon"][0]
            self.attack_range -= self.eq_stats["weapon"][1]
        
        if item.slot_type in self.eq_stats:
            del self.eq_stats[item.slot_type]
