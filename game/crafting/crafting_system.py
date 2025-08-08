"""
Crafting system for creating and upgrading items
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from game.core.settings import Settings
from game.items.item import Item, Weapon, Armor, Consumable

class Recipe:
    """Crafting recipe with materials and result"""
    
    def __init__(self, recipe_id: str, name: str, description: str, 
                 materials: Dict[str, int], result_item: str, result_quantity: int = 1,
                 required_level: int = 1, crafting_time: float = 1.0):
        self.recipe_id = recipe_id
        self.name = name
        self.description = description
        self.materials = materials  # {item_name: quantity}
        self.result_item = result_item
        self.result_quantity = result_quantity
        self.required_level = required_level
        self.crafting_time = crafting_time
        self.unlocked = False
    
    def can_craft(self, player_inventory: List[Item], player_level: int) -> Tuple[bool, str]:
        """Check if recipe can be crafted"""
        if player_level < self.required_level:
            return False, f"Requires level {self.required_level}"
        
        # Check if player has all required materials
        inventory_items = {}
        for item in player_inventory:
            if item.name in inventory_items:
                inventory_items[item.name] += 1
            else:
                inventory_items[item.name] = 1
        
        for material, required_quantity in self.materials.items():
            if material not in inventory_items or inventory_items[material] < required_quantity:
                return False, f"Missing {required_quantity} {material}"
        
        return True, "Can craft"
    
    def consume_materials(self, player_inventory: List[Item]) -> List[Item]:
        """Consume materials from inventory and return updated inventory"""
        materials_needed = self.materials.copy()
        new_inventory = []
        
        for item in player_inventory:
            if item.name in materials_needed and materials_needed[item.name] > 0:
                materials_needed[item.name] -= 1
            else:
                new_inventory.append(item)
        
        return new_inventory

class CraftingSystem:
    """Manages crafting recipes and item creation"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.recipes: Dict[str, Recipe] = {}
        self.crafting_queue: List[Dict[str, Any]] = []
        self.crafting_progress = 0.0
        
        # Initialize recipes
        self._initialize_recipes()
    
    def _initialize_recipes(self):
        """Initialize all crafting recipes"""
        # Weapon recipes
        self.recipes["iron_sword"] = Recipe(
            "iron_sword", "Iron Sword", "A basic iron sword",
            {"Iron Ore": 3, "Wood": 1}, "Iron Sword", 1, 2, 2.0
        )
        
        self.recipes["steel_sword"] = Recipe(
            "steel_sword", "Steel Sword", "A stronger steel sword",
            {"Iron Sword": 1, "Steel": 2, "Leather": 1}, "Steel Sword", 1, 5, 3.0
        )
        
        self.recipes["magic_sword"] = Recipe(
            "magic_sword", "Magic Sword", "A sword imbued with magic",
            {"Steel Sword": 1, "Magic Crystal": 2, "Enchanted Essence": 1}, 
            "Magic Sword", 1, 8, 5.0
        )
        
        # Armor recipes
        self.recipes["leather_armor"] = Recipe(
            "leather_armor", "Leather Armor", "Basic leather protection",
            {"Leather": 4, "Thread": 2}, "Leather Armor", 1, 1, 1.5
        )
        
        self.recipes["chain_mail"] = Recipe(
            "chain_mail", "Chain Mail", "Flexible metal armor",
            {"Iron Ore": 5, "Leather": 2}, "Chain Mail", 1, 3, 2.5
        )
        
        self.recipes["plate_armor"] = Recipe(
            "plate_armor", "Plate Armor", "Heavy protective armor",
            {"Steel": 4, "Chain Mail": 1, "Leather": 3}, "Plate Armor", 1, 6, 4.0
        )
        
        # Consumable recipes
        self.recipes["health_potion"] = Recipe(
            "health_potion", "Health Potion", "Restores health",
            {"Herb": 2, "Water": 1}, "Health Potion", 3, 1, 1.0
        )
        
        self.recipes["strength_potion"] = Recipe(
            "strength_potion", "Strength Potion", "Temporarily increases attack",
            {"Herb": 3, "Iron Ore": 1, "Water": 1}, "Strength Potion", 2, 3, 2.0
        )
        
        self.recipes["magic_potion"] = Recipe(
            "magic_potion", "Magic Potion", "Restores mana and increases magic power",
            {"Magic Crystal": 1, "Herb": 2, "Water": 1}, "Magic Potion", 2, 5, 2.5
        )
        
        # Upgrade recipes
        self.recipes["weapon_upgrade"] = Recipe(
            "weapon_upgrade", "Weapon Upgrade", "Upgrade weapon damage",
            {"Weapon": 1, "Steel": 2, "Magic Crystal": 1}, "Upgraded Weapon", 1, 4, 3.0
        )
        
        self.recipes["armor_upgrade"] = Recipe(
            "armor_upgrade", "Armor Upgrade", "Upgrade armor defense",
            {"Armor": 1, "Steel": 2, "Leather": 2}, "Upgraded Armor", 1, 4, 3.0
        )
    
    def get_available_recipes(self, player_inventory: List[Item], player_level: int) -> List[Recipe]:
        """Get recipes that can be crafted"""
        available = []
        
        for recipe in self.recipes.values():
            can_craft, _ = recipe.can_craft(player_inventory, player_level)
            if can_craft:
                available.append(recipe)
        
        return available
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Get recipe by ID"""
        return self.recipes.get(recipe_id)
    
    def start_crafting(self, recipe_id: str, player_inventory: List[Item], player_level: int) -> Tuple[bool, str]:
        """Start crafting an item"""
        recipe = self.get_recipe_by_id(recipe_id)
        if not recipe:
            return False, "Recipe not found"
        
        can_craft, message = recipe.can_craft(player_inventory, player_level)
        if not can_craft:
            return False, message
        
        # Add to crafting queue
        crafting_job = {
            'recipe_id': recipe_id,
            'recipe': recipe,
            'progress': 0.0,
            'materials_consumed': False
        }
        
        self.crafting_queue.append(crafting_job)
        return True, "Crafting started"
    
    def update_crafting(self, dt: float, player_inventory: List[Item]) -> List[Item]:
        """Update crafting progress and return completed items"""
        completed_items = []
        
        for job in self.crafting_queue[:]:  # Copy list to avoid modification during iteration
            recipe = job['recipe']
            
            # Consume materials if not already done
            if not job['materials_consumed']:
                player_inventory = recipe.consume_materials(player_inventory)
                job['materials_consumed'] = True
            
            # Update progress
            job['progress'] += dt / recipe.crafting_time
            
            # Check if crafting is complete
            if job['progress'] >= 1.0:
                # Create crafted item
                crafted_item = self._create_crafted_item(recipe.result_item)
                if crafted_item:
                    completed_items.append(crafted_item)
                
                # Remove from queue
                self.crafting_queue.remove(job)
        
        return completed_items
    
    def _create_crafted_item(self, item_name: str) -> Optional[Item]:
        """Create a crafted item based on name"""
        if "Sword" in item_name:
            if "Iron" in item_name:
                return Weapon("Iron Sword", "weapon", "common", 15, {"attack": 12})
            elif "Steel" in item_name:
                return Weapon("Steel Sword", "weapon", "uncommon", 20, {"attack": 18})
            elif "Magic" in item_name:
                return Weapon("Magic Sword", "weapon", "rare", 25, {"attack": 25, "magic": 10})
        elif "Armor" in item_name:
            if "Leather" in item_name:
                return Armor("Leather Armor", "armor", "common", 10, {"defense": 8})
            elif "Chain" in item_name:
                return Armor("Chain Mail", "armor", "uncommon", 15, {"defense": 12})
            elif "Plate" in item_name:
                return Armor("Plate Armor", "armor", "rare", 20, {"defense": 18})
        elif "Potion" in item_name:
            if "Health" in item_name:
                return Consumable("Health Potion", "consumable", "common", 5, {"heal": 50})
            elif "Strength" in item_name:
                return Consumable("Strength Potion", "consumable", "uncommon", 8, {"strength": 10})
            elif "Magic" in item_name:
                return Consumable("Magic Potion", "consumable", "rare", 12, {"mana": 100, "magic": 15})
        
        return None
    
    def get_crafting_progress(self) -> List[Dict[str, Any]]:
        """Get current crafting progress"""
        return [
            {
                'recipe_name': job['recipe'].name,
                'progress': job['progress'],
                'time_remaining': job['recipe'].crafting_time * (1 - job['progress'])
            }
            for job in self.crafting_queue
        ]
    
    def cancel_crafting(self, index: int) -> bool:
        """Cancel a crafting job"""
        if 0 <= index < len(self.crafting_queue):
            self.crafting_queue.pop(index)
            return True
        return False
    
    def unlock_recipe(self, recipe_id: str):
        """Unlock a recipe (for progression)"""
        if recipe_id in self.recipes:
            self.recipes[recipe_id].unlocked = True
    
    def get_recipe_categories(self) -> Dict[str, List[Recipe]]:
        """Get recipes organized by category"""
        categories = {
            'weapons': [],
            'armor': [],
            'consumables': [],
            'upgrades': []
        }
        
        for recipe in self.recipes.values():
            if "Sword" in recipe.result_item or "Weapon" in recipe.result_item:
                categories['weapons'].append(recipe)
            elif "Armor" in recipe.result_item:
                categories['armor'].append(recipe)
            elif "Potion" in recipe.result_item:
                categories['consumables'].append(recipe)
            elif "Upgrade" in recipe.name:
                categories['upgrades'].append(recipe)
        
        return categories
    
    def get_material_requirements(self, recipe_id: str) -> Dict[str, int]:
        """Get material requirements for a recipe"""
        recipe = self.get_recipe_by_id(recipe_id)
        return recipe.materials if recipe else {}
    
    def can_afford_recipe(self, recipe_id: str, player_inventory: List[Item]) -> bool:
        """Check if player can afford a recipe"""
        recipe = self.get_recipe_by_id(recipe_id)
        if not recipe:
            return False
        
        can_craft, _ = recipe.can_craft(player_inventory, 1)  # Ignore level requirement
        return can_craft
