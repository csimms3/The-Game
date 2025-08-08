"""
Item system
"""

import pygame
import random
from typing import Dict, Any, Optional
from game.core.settings import Settings

class Item:
    """Base item class"""
    
    def __init__(self, name: str, item_type: str, rarity: str = "common"):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.description = ""
        self.value = 0
        
        # Stats
        self.attack_bonus = 0
        self.defense_bonus = 0
        self.health_bonus = 0
        self.speed_bonus = 0
        
        # Visual
        self.sprite = None
        self.color = self._get_rarity_color()
        
        # Create sprite
        self._create_sprite()
    
    def _get_rarity_color(self) -> tuple:
        """Get color based on rarity"""
        colors = {
            "common": (192, 192, 192),    # Gray
            "uncommon": (0, 255, 0),      # Green
            "rare": (0, 100, 255),        # Blue
            "epic": (150, 0, 255),        # Purple
            "legendary": (255, 165, 0)    # Orange
        }
        return colors.get(self.rarity, colors["common"])
    
    def _create_sprite(self):
        """Create item sprite"""
        self.sprite = pygame.Surface((16, 16))
        self.sprite.fill(self.color)
        pygame.draw.rect(self.sprite, (255, 255, 255), (2, 2, 12, 12))
    
    def use(self, player) -> bool:
        """Use the item"""
        return False
    
    def get_description(self) -> str:
        """Get item description"""
        desc = f"{self.name} ({self.rarity.title()})\n"
        desc += f"Type: {self.item_type.title()}\n"
        
        if self.attack_bonus > 0:
            desc += f"Attack: +{self.attack_bonus}\n"
        if self.defense_bonus > 0:
            desc += f"Defense: +{self.defense_bonus}\n"
        if self.health_bonus > 0:
            desc += f"Health: +{self.health_bonus}\n"
        if self.speed_bonus > 0:
            desc += f"Speed: +{self.speed_bonus}\n"
        
        return desc

class Weapon(Item):
    """Weapon items"""
    
    def __init__(self, name: str, attack_bonus: int, rarity: str = "common"):
        super().__init__(name, "weapon", rarity)
        self.attack_bonus = attack_bonus
        self.value = attack_bonus * 10
        
        # Weapon specific
        self.durability = 100
        self.max_durability = 100
    
    def use(self, player) -> bool:
        """Equip weapon"""
        return player.equip_item(self)

class Armor(Item):
    """Armor items"""
    
    def __init__(self, name: str, defense_bonus: int, health_bonus: int = 0, rarity: str = "common"):
        super().__init__(name, "armor", rarity)
        self.defense_bonus = defense_bonus
        self.health_bonus = health_bonus
        self.value = (defense_bonus + health_bonus) * 8
        
        # Armor specific
        self.durability = 100
        self.max_durability = 100
    
    def use(self, player) -> bool:
        """Equip armor"""
        return player.equip_item(self)

class Consumable(Item):
    """Consumable items"""
    
    def __init__(self, name: str, effect_type: str, effect_value: int, rarity: str = "common"):
        super().__init__(name, "consumable", rarity)
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.value = effect_value * 5
    
    def use(self, player) -> bool:
        """Use consumable"""
        if self.effect_type == "heal":
            player.heal(self.effect_value)
            return True
        elif self.effect_type == "speed":
            player.speed += self.effect_value
            return True
        return False

class ItemFactory:
    """Factory for creating items"""
    
    @staticmethod
    def create_random_weapon(level: int = 1) -> Weapon:
        """Create a random weapon"""
        weapons = [
            ("Rusty Sword", 5),
            ("Iron Sword", 8),
            ("Steel Sword", 12),
            ("Magic Sword", 18),
            ("Legendary Blade", 25)
        ]
        
        name, base_attack = random.choice(weapons)
        attack_bonus = base_attack + (level - 1) * 2
        
        # Determine rarity based on level
        if level >= 10:
            rarity = random.choices(["epic", "legendary"], weights=[0.7, 0.3])[0]
        elif level >= 5:
            rarity = random.choices(["rare", "epic"], weights=[0.8, 0.2])[0]
        else:
            rarity = random.choices(["common", "uncommon"], weights=[0.7, 0.3])[0]
        
        return Weapon(name, attack_bonus, rarity)
    
    @staticmethod
    def create_random_armor(level: int = 1) -> Armor:
        """Create a random armor"""
        armors = [
            ("Leather Armor", 3, 10),
            ("Chain Mail", 5, 20),
            ("Plate Armor", 8, 30),
            ("Magic Armor", 12, 50),
            ("Dragon Scale", 15, 80)
        ]
        
        name, base_defense, base_health = random.choice(armors)
        defense_bonus = base_defense + (level - 1)
        health_bonus = base_health + (level - 1) * 5
        
        # Determine rarity
        if level >= 10:
            rarity = random.choices(["epic", "legendary"], weights=[0.7, 0.3])[0]
        elif level >= 5:
            rarity = random.choices(["rare", "epic"], weights=[0.8, 0.2])[0]
        else:
            rarity = random.choices(["common", "uncommon"], weights=[0.7, 0.3])[0]
        
        return Armor(name, defense_bonus, health_bonus, rarity)
    
    @staticmethod
    def create_random_consumable() -> Consumable:
        """Create a random consumable"""
        consumables = [
            ("Health Potion", "heal", 50),
            ("Greater Health Potion", "heal", 100),
            ("Speed Potion", "speed", 2),
            ("Elixir of Life", "heal", 200)
        ]
        
        name, effect_type, effect_value = random.choice(consumables)
        rarity = random.choice(["common", "uncommon", "rare"])
        
        return Consumable(name, effect_type, effect_value, rarity)
    
    @staticmethod
    def create_random_item(level: int = 1) -> Item:
        """Create a random item"""
        item_types = ["weapon", "armor", "consumable"]
        weights = [0.4, 0.4, 0.2]  # 40% weapon, 40% armor, 20% consumable
        
        item_type = random.choices(item_types, weights=weights)[0]
        
        if item_type == "weapon":
            return ItemFactory.create_random_weapon(level)
        elif item_type == "armor":
            return ItemFactory.create_random_armor(level)
        else:
            return ItemFactory.create_random_consumable()
    
    @staticmethod
    def create_item(item_name: str) -> Optional[Item]:
        """Create a specific item by name"""
        item_definitions = {
            # Weapons
            "Rusty Sword": lambda: Weapon("Rusty Sword", 5, "common"),
            "Iron Sword": lambda: Weapon("Iron Sword", 8, "uncommon"),
            "Steel Sword": lambda: Weapon("Steel Sword", 12, "rare"),
            "Magic Sword": lambda: Weapon("Magic Sword", 18, "epic"),
            "Legendary Blade": lambda: Weapon("Legendary Blade", 25, "legendary"),
            
            # Armor
            "Leather Armor": lambda: Armor("Leather Armor", 3, 10, "common"),
            "Chain Mail": lambda: Armor("Chain Mail", 5, 20, "uncommon"),
            "Plate Armor": lambda: Armor("Plate Armor", 8, 30, "rare"),
            "Magic Armor": lambda: Armor("Magic Armor", 12, 50, "epic"),
            "Dragon Scale": lambda: Armor("Dragon Scale", 15, 80, "legendary"),
            
            # Consumables
            "Health Potion": lambda: Consumable("Health Potion", "heal", 50, "common"),
            "Magic Potion": lambda: Consumable("Magic Potion", "heal", 100, "uncommon"),
            "Strength Potion": lambda: Consumable("Strength Potion", "speed", 2, "rare"),
            "Greater Health Potion": lambda: Consumable("Greater Health Potion", "heal", 100, "uncommon"),
            "Speed Potion": lambda: Consumable("Speed Potion", "speed", 2, "common"),
            "Elixir of Life": lambda: Consumable("Elixir of Life", "heal", 200, "epic")
        }
        
        if item_name in item_definitions:
            return item_definitions[item_name]()
        else:
            # Return a default health potion if item not found
            return Consumable("Health Potion", "heal", 50, "common")
