"""
Test suite for the game
"""

import unittest
import pygame
import sys
import os

# Add the game directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from game.core.settings import Settings
from game.entities.player import Player
from game.entities.enemy import Enemy
from game.items.item import Item, Weapon, Armor, Consumable, ItemFactory
from game.world.world_generator import WorldGenerator

class TestSettings(unittest.TestCase):
    """Test settings configuration"""
    
    def setUp(self):
        self.settings = Settings()
    
    def test_settings_initialization(self):
        """Test that settings are properly initialized"""
        self.assertEqual(self.settings.SCREEN_WIDTH, 1280)
        self.assertEqual(self.settings.SCREEN_HEIGHT, 720)
        self.assertEqual(self.settings.FPS, 60)
        self.assertEqual(self.settings.TILE_SIZE, 32)
    
    def test_color_constants(self):
        """Test color constants"""
        self.assertEqual(self.settings.BLACK, (0, 0, 0))
        self.assertEqual(self.settings.WHITE, (255, 255, 255))
        self.assertEqual(self.settings.RED, (255, 0, 0))
        self.assertEqual(self.settings.GREEN, (0, 255, 0))
        self.assertEqual(self.settings.BLUE, (0, 0, 255))

class TestPlayer(unittest.TestCase):
    """Test player functionality"""
    
    def setUp(self):
        pygame.init()
        self.settings = Settings()
        self.player = Player(100, 100, self.settings)
    
    def tearDown(self):
        pygame.quit()
    
    def test_player_initialization(self):
        """Test player initialization"""
        self.assertEqual(self.player.x, 100)
        self.assertEqual(self.player.y, 100)
        self.assertEqual(self.player.health, self.player.max_health)
        self.assertTrue(self.player.alive)
        self.assertEqual(self.player.level, 1)
        self.assertEqual(self.player.experience, 0)
    
    def test_player_movement(self):
        """Test player movement"""
        initial_x = self.player.x
        initial_y = self.player.y
        
        # Test movement
        self.player.move(10, 5)
        self.assertEqual(self.player.x, initial_x + 10)
        self.assertEqual(self.player.y, initial_y + 5)
    
    def test_player_combat(self):
        """Test player combat"""
        enemy = Enemy(150, 100, self.settings)
        initial_health = enemy.health
        
        # Test attack
        self.player.attack(enemy)
        self.assertLess(enemy.health, initial_health)
    
    def test_player_leveling(self):
        """Test player leveling system"""
        initial_level = self.player.level
        initial_max_health = self.player.max_health
        
        # Gain enough experience to level up
        self.player.gain_experience(100)
        
        self.assertEqual(self.player.level, initial_level + 1)
        self.assertGreater(self.player.max_health, initial_max_health)

class TestEnemy(unittest.TestCase):
    """Test enemy functionality"""
    
    def setUp(self):
        pygame.init()
        self.settings = Settings()
        self.enemy = Enemy(200, 200, self.settings, "goblin")
        self.player = Player(100, 100, self.settings)
    
    def tearDown(self):
        pygame.quit()
    
    def test_enemy_initialization(self):
        """Test enemy initialization"""
        self.assertEqual(self.enemy.enemy_type, "goblin")
        self.assertTrue(self.enemy.alive)
        self.assertIsNone(self.enemy.target)
    
    def test_enemy_detection(self):
        """Test enemy detection range"""
        # Enemy should detect player when close
        self.enemy.x = self.player.x + 100
        self.enemy.y = self.player.y + 100
        
        self.assertTrue(self.enemy.can_detect_target(self.player))
    
    def test_enemy_combat(self):
        """Test enemy combat"""
        initial_health = self.player.health
        
        # Set enemy to attack player
        self.enemy.set_target(self.player)
        self.enemy.attack_cooldown = 0  # Reset cooldown
        
        # Simulate attack
        self.enemy._attack_target()
        
        self.assertLess(self.player.health, initial_health)

class TestItems(unittest.TestCase):
    """Test item system"""
    
    def setUp(self):
        pygame.init()
        self.settings = Settings()
        self.player = Player(100, 100, self.settings)
    
    def tearDown(self):
        pygame.quit()
    
    def test_weapon_creation(self):
        """Test weapon creation"""
        weapon = Weapon("Test Sword", 10, "rare")
        self.assertEqual(weapon.name, "Test Sword")
        self.assertEqual(weapon.attack_bonus, 10)
        self.assertEqual(weapon.rarity, "rare")
        self.assertEqual(weapon.item_type, "weapon")
    
    def test_armor_creation(self):
        """Test armor creation"""
        armor = Armor("Test Armor", 5, 20, "uncommon")
        self.assertEqual(armor.name, "Test Armor")
        self.assertEqual(armor.defense_bonus, 5)
        self.assertEqual(armor.health_bonus, 20)
        self.assertEqual(armor.rarity, "uncommon")
    
    def test_consumable_creation(self):
        """Test consumable creation"""
        potion = Consumable("Health Potion", "heal", 50, "common")
        self.assertEqual(potion.name, "Health Potion")
        self.assertEqual(potion.effect_type, "heal")
        self.assertEqual(potion.effect_value, 50)
    
    def test_item_factory(self):
        """Test item factory"""
        weapon = ItemFactory.create_random_weapon(5)
        self.assertIsInstance(weapon, Weapon)
        self.assertGreater(weapon.attack_bonus, 0)
        
        armor = ItemFactory.create_random_armor(3)
        self.assertIsInstance(armor, Armor)
        self.assertGreater(armor.defense_bonus, 0)
        
        consumable = ItemFactory.create_random_consumable()
        self.assertIsInstance(consumable, Consumable)
    
    def test_player_inventory(self):
        """Test player inventory system"""
        initial_inventory_size = len(self.player.inventory)
        
        # Add item to inventory
        weapon = Weapon("Test Weapon", 5)
        success = self.player.add_item_to_inventory(weapon)
        
        self.assertTrue(success)
        self.assertEqual(len(self.player.inventory), initial_inventory_size + 1)
        
        # Test inventory limit
        for i in range(25):  # More than max_inventory_size
            item = ItemFactory.create_random_item()
            self.player.add_item_to_inventory(item)
        
        self.assertLessEqual(len(self.player.inventory), self.player.max_inventory_size)

class TestWorldGenerator(unittest.TestCase):
    """Test world generation"""
    
    def setUp(self):
        pygame.init()
        self.settings = Settings()
        self.world = WorldGenerator(self.settings)
    
    def tearDown(self):
        pygame.quit()
    
    def test_world_initialization(self):
        """Test world initialization"""
        self.assertIsNotNone(self.world.terrain_map)
        self.assertIsNotNone(self.world.structures)
        self.assertIsNotNone(self.world.items)
        self.assertGreater(len(self.world.terrain_map), 0)
    
    def test_terrain_generation(self):
        """Test terrain generation"""
        # Check that terrain map has valid terrain types
        valid_terrain_types = ['grass', 'forest', 'water', 'mountain', 'desert', 'snow']
        
        for row in self.world.terrain_map:
            for terrain_type in row:
                self.assertIn(terrain_type, valid_terrain_types)
    
    def test_walkable_terrain(self):
        """Test walkable terrain detection"""
        # Test some positions
        self.assertTrue(self.world.is_walkable_at(100, 100))
        self.assertTrue(self.world.is_walkable_at(500, 500))
    
    def test_terrain_at_position(self):
        """Test getting terrain at position"""
        terrain_type = self.world.get_terrain_at(100, 100)
        self.assertIsInstance(terrain_type, str)
        self.assertIn(terrain_type, self.world.terrain_types.keys())

class TestGameIntegration(unittest.TestCase):
    """Integration tests for game components"""
    
    def setUp(self):
        pygame.init()
        self.settings = Settings()
        self.player = Player(100, 100, self.settings)
        self.enemy = Enemy(200, 200, self.settings)
        self.world = WorldGenerator(self.settings)
    
    def tearDown(self):
        pygame.quit()
    
    def test_player_enemy_interaction(self):
        """Test player and enemy interaction"""
        # Test collision detection
        self.assertFalse(self.player.is_colliding_with(self.enemy))
        
        # Move enemy close to player
        self.enemy.x = self.player.x + 30
        self.enemy.y = self.player.y + 30
        
        self.assertTrue(self.player.is_colliding_with(self.enemy))
    
    def test_combat_system(self):
        """Test complete combat system"""
        initial_player_health = self.player.health
        initial_enemy_health = self.enemy.health
        
        # Player attacks enemy
        self.player.attack(self.enemy)
        self.assertLess(self.enemy.health, initial_enemy_health)
        
        # Enemy attacks player
        self.enemy.set_target(self.player)
        self.enemy.attack_cooldown = 0
        self.enemy._attack_target()
        self.assertLess(self.player.health, initial_player_health)
    
    def test_item_pickup_system(self):
        """Test item pickup system"""
        weapon = Weapon("Test Weapon", 10)
        
        # Add item to player inventory
        success = self.player.add_item_to_inventory(weapon)
        self.assertTrue(success)
        self.assertIn(weapon, self.player.inventory)
        
        # Equip weapon
        equip_success = self.player.equip_item(weapon)
        self.assertTrue(equip_success)
        self.assertEqual(self.player.equipped_weapon, weapon)
        self.assertNotIn(weapon, self.player.inventory)

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSettings,
        TestPlayer,
        TestEnemy,
        TestItems,
        TestWorldGenerator,
        TestGameIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
