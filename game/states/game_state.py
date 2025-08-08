"""
Main game state
"""

import pygame
import math
from typing import List, Tuple
from game.states.base_state import BaseState
from game.entities.player import Player
from game.entities.enemy import Enemy, EnemySpawner
from game.world.world_generator import WorldGenerator
from game.items.item import ItemFactory
from game.ui.hud import HUD
from game.ui.inventory import InventoryUI
import random

class GameState(BaseState):
    """Main gameplay state"""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        
        # Game world
        self.world_generator = WorldGenerator(self.settings)
        
        # Player
        self.player = Player(1000, 1000, self.settings)
        
        # Enemies
        self.enemies: List[Enemy] = []
        self.enemy_spawner = EnemySpawner(self.settings)
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Game state
        self.game_mode = None
        self.game_time = 0
        self.score = 0
        
        # UI systems
        self.hud = HUD(self.settings)
        self.inventory_ui = InventoryUI(self.settings)
        
        # Input
        self.keys_pressed = set()
        
        # Combat
        self.combat_cooldown = 0
        
        # Items
        self.items = self.world_generator.items.copy()
        
        # Messages
        self.messages = []
        self.message_timer = 0
    
    def enter(self):
        """Called when entering game state"""
        self.logger.info("Entering game state")
        self.game_mode = self.game_engine.game_mode
        
        # Initialize some enemies
        for _ in range(5):
            self._spawn_enemy()
    
    def exit(self):
        """Called when exiting game state"""
        self.logger.info("Exiting game state")
    
    def handle_event(self, event):
        """Handle game events"""
        # Check inventory first
        if self.inventory_ui.handle_event(event, self.player):
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_engine.change_state('pause')
            elif event.key == pygame.K_SPACE:
                self._attack_nearest_enemy()
            elif event.key == pygame.K_e:
                self._pickup_nearby_items()
            elif event.key == pygame.K_i:
                self.inventory_ui.toggle()
            elif event.key == pygame.K_m:
                self._show_map()
        
        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed.remove(event.key)
    
    def update(self, dt: float):
        """Update game logic"""
        self.game_time += dt
        
        # Update player
        self.player.update(dt)
        
        # Update camera to follow player
        self._update_camera()
        
        # Update enemies
        self._update_enemies(dt)
        
        # Update enemy spawner
        self.enemy_spawner.update(dt, self.enemies, self.player.get_center())
        
        # Update combat
        if self.combat_cooldown > 0:
            self.combat_cooldown -= dt
        
        # Update messages
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.messages.pop(0) if self.messages else None
        
        # Check player death
        if not self.player.alive:
            self._game_over()
    
    def render(self, screen):
        """Render the game"""
        # Render world
        self.world_generator.render_world(screen, (self.camera_x, self.camera_y))
        
        # Render enemies
        for enemy in self.enemies:
            if enemy.alive:
                enemy.render(screen, (self.camera_x, self.camera_y))
        
        # Render player
        self.player.render(screen, (self.camera_x, self.camera_y))
        
        # Render HUD
        self._render_hud(screen)
        
        # Render inventory
        self.inventory_ui.render(screen, self.player)
    
    def _render_hud(self, screen):
        """Render the HUD"""
        # Health bar
        self.hud.render_health_bar(screen, self.player.health, self.player.max_health, 10, 10)
        
        # Experience bar
        self.hud.render_exp_bar(screen, self.player.experience, self.player.experience_to_next_level, 10, 35)
        
        # Stats panel
        self.hud.render_stats_panel(screen, self.player, 10, 60)
        
        # Minimap
        self.hud.render_minimap(screen, self.world_generator, self.player, 
                               (self.camera_x, self.camera_y), 
                               self.settings.SCREEN_WIDTH - 160, 10)
        
        # Message log
        self.hud.render_message_log(screen, self.messages, 10, 
                                   self.settings.SCREEN_HEIGHT - 150)
        
        # Controls help
        self.hud.render_controls_help(screen, self.settings.SCREEN_WIDTH - 200, 10)
    
    def _update_camera(self):
        """Update camera to follow player"""
        target_x = self.player.x - self.settings.SCREEN_WIDTH // 2
        target_y = self.player.y - self.settings.SCREEN_HEIGHT // 2
        
        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # Clamp camera to world bounds
        self.camera_x = max(0, min(self.camera_x, self.world_generator.world_width - self.settings.SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.world_generator.world_height - self.settings.SCREEN_HEIGHT))
    
    def _update_enemies(self, dt: float):
        """Update all enemies"""
        # Remove dead enemies
        self.enemies = [enemy for enemy in self.enemies if enemy.alive]
        
        # Update each enemy
        for enemy in self.enemies:
            enemy.update(dt)
            
            # Check if enemy can detect player
            if enemy.can_detect_target(self.player):
                enemy.set_target(self.player)
            
            # Check collision with player
            if enemy.is_colliding_with(self.player):
                if enemy.attack_cooldown <= 0:
                    enemy._attack_target()
    
    def _spawn_enemy(self):
        """Spawn a new enemy"""
        # Spawn enemy away from player
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(200, 400)
        
        spawn_x = self.player.x + math.cos(angle) * distance
        spawn_y = self.player.y + math.sin(angle) * distance
        
        # Ensure spawn location is walkable
        if self.world_generator.is_walkable_at(spawn_x, spawn_y):
            enemy = Enemy(spawn_x, spawn_y, self.settings)
            self.enemies.append(enemy)
    
    def _attack_nearest_enemy(self):
        """Attack the nearest enemy"""
        if self.combat_cooldown > 0:
            return
        
        nearest_enemy = None
        nearest_distance = float('inf')
        
        for enemy in self.enemies:
            if enemy.alive:
                distance = self.player.distance_to(enemy)
                if distance < nearest_distance and distance <= self.player.attack_range:
                    nearest_distance = distance
                    nearest_enemy = enemy
        
        if nearest_enemy:
            if self.player.attack(nearest_enemy):
                self.combat_cooldown = 0.5
                self._add_message(f"Attacked {nearest_enemy.enemy_type}!")
                
                # Check if enemy died
                if not nearest_enemy.alive:
                    self.score += 10
                    self.player.gain_experience(20)
                    self._add_message(f"Defeated {nearest_enemy.enemy_type}! +20 XP")
    
    def _pickup_nearby_items(self):
        """Pickup items near the player"""
        pickup_range = 50
        items_to_remove = []
        
        for item_data in self.items:
            distance = math.sqrt((self.player.x - item_data['x']) ** 2 + 
                               (self.player.y - item_data['y']) ** 2)
            
            if distance <= pickup_range:
                if self.player.add_item_to_inventory(item_data['item']):
                    items_to_remove.append(item_data)
                    self._add_message(f"Picked up {item_data['item'].name}!")
                else:
                    self._add_message("Inventory full!")
        
        # Remove picked up items
        for item_data in items_to_remove:
            self.items.remove(item_data)
    
    def _show_map(self):
        """Show map (placeholder)"""
        self._add_message("Map: Press M to view world map")
    
    def _game_over(self):
        """Handle game over"""
        self._add_message("Game Over! You have been defeated.")
        # TODO: Implement game over screen
    
    def _add_message(self, message: str):
        """Add a message to the message log"""
        self.messages.append(message)
        self.message_timer = 3.0  # Show message for 3 seconds
        
        # Limit message log
        if len(self.messages) > 5:
            self.messages.pop(0)
