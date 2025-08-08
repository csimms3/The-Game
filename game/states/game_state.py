"""
Main game state
"""

import pygame
import math
from typing import List, Tuple
from game.states.base_state import BaseState
from game.entities.player import Player
from game.entities.enemy import Enemy, EnemySpawner
from game.entities.advanced_enemies import BossEnemy, EliteEnemy
from game.world.world_generator import WorldGenerator
from game.items.item import ItemFactory
from game.ui.hud import HUD
from game.ui.inventory import InventoryUI
from game.effects.particles import ParticleSystem
from game.utils.spatial_hash import RenderOptimizer
from game.audio.sound_manager import SoundManager
from game.quests.quest_system import QuestSystem
from game.crafting.crafting_system import CraftingSystem
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
        
        # Effects and optimization
        self.particle_system = ParticleSystem(self.settings)
        self.render_optimizer = RenderOptimizer(self.settings)
        
        # Audio system
        self.sound_manager = SoundManager(self.settings)
        
        # Quest system
        self.quest_system = QuestSystem(self.settings)
        
        # Crafting system
        self.crafting_system = CraftingSystem(self.settings)
        
        # Input
        self.keys_pressed = set()
        
        # Combat
        self.combat_cooldown = 0
        
        # Items
        self.items = self.world_generator.items.copy()
        
        # Messages
        self.messages = []
        self.message_timer = 0
        
        # Performance tracking
        self.frame_times = []
        self.fps_counter = 0
        self.current_fps = 60
        
        # Initialize spatial optimization
        self._initialize_spatial_optimization()
        
        # Start background music
        self.sound_manager.play_music("exploration_theme")
    
    def _initialize_spatial_optimization(self):
        """Initialize spatial optimization for entities"""
        # Add player to spatial hash
        self.render_optimizer.add_entity(self.player)
        
        # Add initial enemies
        for enemy in self.enemies:
            self.render_optimizer.add_entity(enemy)
    
    def enter(self):
        """Called when entering game state"""
        self.logger.info("Entering game state")
        self.game_mode = self.game_engine.game_mode
        
        # Initialize some enemies
        for _ in range(5):
            self._spawn_enemy()
        
        # Spawn some elite enemies
        for _ in range(2):
            self._spawn_elite_enemy()
        
        # Spawn a boss (rare)
        if random.random() < 0.3:
            self._spawn_boss()
    
    def exit(self):
        """Called when exiting game state"""
        self.logger.info("Exiting game state")
        self.sound_manager.stop_music()
    
    def handle_event(self, event):
        """Handle game events"""
        # Check inventory first
        if self.inventory_ui.handle_event(event, self.player):
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.sound_manager.play_ui_sounds("select")
                self.game_engine.change_state('pause')
            elif event.key == pygame.K_SPACE:
                self._attack_nearest_enemy()
            elif event.key == pygame.K_e:
                self._pickup_nearby_items()
            elif event.key == pygame.K_i:
                self.inventory_ui.toggle()
                self.sound_manager.play_ui_sounds("select")
            elif event.key == pygame.K_m:
                self._show_map()
            elif event.key == pygame.K_q:
                self._open_quest_log()
            elif event.key == pygame.K_c:
                self._open_crafting_menu()
            elif event.key == pygame.K_f:
                self._use_health_potion()
        
        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed.remove(event.key)
    
    def update(self, dt: float):
        """Update game logic"""
        self.game_time += dt
        
        # Update performance tracking
        self._update_performance_tracking(dt)
        
        # Update player
        self.player.update(dt)
        
        # Update camera to follow player
        self._update_camera()
        
        # Update spatial optimization
        self.render_optimizer.update_visible_entities(self.camera_x, self.camera_y)
        
        # Update enemies
        self._update_enemies(dt)
        
        # Update enemy spawner
        self.enemy_spawner.update(dt, self.enemies, self.player.get_center())
        
        # Update particle system
        self.particle_system.update(dt)
        
        # Update quest system
        self._update_quest_progress()
        
        # Update crafting system
        completed_items = self.crafting_system.update_crafting(dt, self.player.inventory)
        for item in completed_items:
            self.player.add_item_to_inventory(item)
            self._add_message(f"Crafted {item.name}!")
            self.sound_manager.play_ui_sounds("confirm")
        
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
        
        # Render visible enemies (optimized)
        visible_entities = self.render_optimizer.get_visible_entities()
        for enemy in self.enemies:
            if enemy.alive and enemy in visible_entities:
                enemy.render(screen, (self.camera_x, self.camera_y))
        
        # Render player
        self.player.render(screen, (self.camera_x, self.camera_y))
        
        # Render particles
        self.particle_system.render(screen, (self.camera_x, self.camera_y))
        
        # Render HUD
        self._render_hud(screen)
        
        # Render inventory
        self.inventory_ui.render(screen, self.player)
        
        # Render performance info (debug)
        if self.settings.DEBUG_MODE:
            self._render_debug_info(screen)
    
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
        
        # Quest info
        self._render_quest_info(screen)
        
        # Crafting progress
        self._render_crafting_progress(screen)
    
    def _render_quest_info(self, screen):
        """Render quest information"""
        quest_summary = self.quest_system.get_quest_summary()
        active_quests = len(self.quest_system.active_quests)
        
        if active_quests > 0:
            font = pygame.font.Font(None, 20)
            quest_text = font.render(f"Active Quests: {active_quests}", True, (255, 255, 255))
            screen.blit(quest_text, (10, self.settings.SCREEN_HEIGHT - 200))
    
    def _render_crafting_progress(self, screen):
        """Render crafting progress"""
        crafting_jobs = self.crafting_system.get_crafting_progress()
        
        if crafting_jobs:
            font = pygame.font.Font(None, 18)
            y_offset = 10
            
            for job in crafting_jobs:
                progress_text = f"Crafting: {job['recipe_name']} ({job['progress']:.1%})"
                text_surface = font.render(progress_text, True, (255, 255, 0))
                screen.blit(text_surface, (10, self.settings.SCREEN_HEIGHT - 180 + y_offset))
                y_offset += 20
    
    def _render_debug_info(self, screen):
        """Render debug information"""
        font = pygame.font.Font(None, 16)
        
        debug_info = [
            f"FPS: {self.current_fps:.1f}",
            f"Entities: {len(self.enemies)}",
            f"Particles: {len(self.particle_system.particles)}",
            f"Camera: ({self.camera_x:.0f}, {self.camera_y:.0f})",
            f"Player: ({self.player.x:.0f}, {self.player.y:.0f})"
        ]
        
        for i, info in enumerate(debug_info):
            text = font.render(info, True, (255, 255, 255))
            screen.blit(text, (10, 200 + i * 15))
    
    def _update_performance_tracking(self, dt: float):
        """Update performance tracking"""
        self.frame_times.append(dt)
        self.fps_counter += 1
        
        # Calculate FPS every 60 frames
        if self.fps_counter >= 60:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 60
            self.frame_times.clear()
            self.fps_counter = 0
    
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
        dead_enemies = [enemy for enemy in self.enemies if not enemy.alive]
        for enemy in dead_enemies:
            self.render_optimizer.remove_entity(enemy)
            # Create death effect
            self.particle_system.create_explosion_effect(enemy.x, enemy.y, 0.5)
            self.sound_manager.play_ambient_sounds("explosion")
            
            # Update quest progress
            self.quest_system.on_enemy_killed(enemy.enemy_type)
        
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
                    # Create damage effect on player
                    self.particle_system.create_damage_effect(self.player.x, self.player.y, 10)
                    self.sound_manager.play_combat_sounds("damage")
    
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
            self.render_optimizer.add_entity(enemy)
    
    def _spawn_elite_enemy(self):
        """Spawn an elite enemy"""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(300, 500)
        
        spawn_x = self.player.x + math.cos(angle) * distance
        spawn_y = self.player.y + math.sin(angle) * distance
        
        if self.world_generator.is_walkable_at(spawn_x, spawn_y):
            elite_types = ["warrior", "archer", "mage", "assassin"]
            elite_type = random.choice(elite_types)
            enemy = EliteEnemy(spawn_x, spawn_y, self.settings, elite_type)
            self.enemies.append(enemy)
            self.render_optimizer.add_entity(enemy)
    
    def _spawn_boss(self):
        """Spawn a boss enemy"""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(400, 600)
        
        spawn_x = self.player.x + math.cos(angle) * distance
        spawn_y = self.player.y + math.sin(angle) * distance
        
        if self.world_generator.is_walkable_at(spawn_x, spawn_y):
            boss_types = ["dragon", "lich", "golem"]
            boss_type = random.choice(boss_types)
            enemy = BossEnemy(spawn_x, spawn_y, self.settings, boss_type)
            self.enemies.append(enemy)
            self.render_optimizer.add_entity(enemy)
            self._add_message(f"A {boss_type.title()} boss has appeared!")
    
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
                self.sound_manager.play_combat_sounds("attack")
                
                # Create combat effect
                self.particle_system.create_combat_effect(nearest_enemy.x, nearest_enemy.y, "slash")
                
                # Check if enemy died
                if not nearest_enemy.alive:
                    self.score += 10
                    self.player.gain_experience(20)
                    self._add_message(f"Defeated {nearest_enemy.enemy_type}! +20 XP")
                    self.sound_manager.play_combat_sounds("enemy_death")
                    
                    # Create level up effect if player leveled up
                    if self.player.level > getattr(self, '_last_level', 0):
                        self.particle_system.create_level_up_effect(self.player.x, self.player.y)
                        self.sound_manager.play_ui_sounds("level_up")
                        self._last_level = self.player.level
    
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
                    self.sound_manager.play_ui_sounds("pickup")
                    
                    # Create pickup effect
                    self.particle_system.create_item_pickup_effect(
                        item_data['x'], item_data['y'], item_data['item'].rarity
                    )
                    
                    # Update quest progress
                    self.quest_system.on_item_collected(item_data['item'].name)
                else:
                    self._add_message("Inventory full!")
        
        # Remove picked up items
        for item_data in items_to_remove:
            self.items.remove(item_data)
    
    def _use_health_potion(self):
        """Use a health potion"""
        health_potion = None
        for item in self.player.inventory:
            if item.name == "Health Potion":
                health_potion = item
                break
        
        if health_potion:
            self.player.inventory.remove(health_potion)
            heal_amount = 50
            self.player.heal(heal_amount)
            self._add_message(f"Used Health Potion! +{heal_amount} HP")
            self.sound_manager.play_combat_sounds("heal")
            self.particle_system.create_heal_effect(self.player.x, self.player.y, heal_amount)
        else:
            self._add_message("No Health Potion available!")
    
    def _open_quest_log(self):
        """Open quest log (placeholder)"""
        self._add_message("Quest Log: Press Q to view active quests")
    
    def _open_crafting_menu(self):
        """Open crafting menu (placeholder)"""
        self._add_message("Crafting: Press C to open crafting menu")
    
    def _show_map(self):
        """Show map (placeholder)"""
        self._add_message("Map: Press M to view world map")
    
    def _update_quest_progress(self):
        """Update quest progress based on player actions"""
        # Check for level up
        if self.player.level > getattr(self, '_last_quest_level', 0):
            self.quest_system.on_level_up(self.player.level)
            self._last_quest_level = self.player.level
    
    def _game_over(self):
        """Handle game over"""
        self._add_message("Game Over! You have been defeated.")
        self.sound_manager.play_combat_sounds("damage")
        # TODO: Implement game over screen
    
    def _add_message(self, message: str):
        """Add a message to the message log"""
        self.messages.append(message)
        self.message_timer = 3.0  # Show message for 3 seconds
        
        # Limit message log
        if len(self.messages) > 5:
            self.messages.pop(0)
