"""
Main game state with complete feature implementation
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
from game.graphics.renderer import Renderer
from game.graphics.ui_system import UISystem
import random

class GameState(BaseState):
    """Main gameplay state with complete feature implementation"""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.player = Player(1000, 1000, self.settings)
        self.enemies = []
        self.items = []
        self.world_generator = WorldGenerator(self.settings)
        self.camera_x = 0
        self.camera_y = 0
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.camera_speed = 5.0
        
        # Input handling
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        
        # Game systems
        self.hud = HUD(self.settings)
        self.inventory_ui = InventoryUI(self.settings)
        self.particle_system = ParticleSystem(self.settings)
        self.render_optimizer = RenderOptimizer(self.settings)
        self.sound_manager = SoundManager(self.settings)
        self.quest_system = QuestSystem(self.settings)
        self.crafting_system = CraftingSystem(self.settings)
        self.renderer = Renderer(self.settings)
        self.ui_system = UISystem(self.settings)
        
        # Initialize spatial optimization
        self._initialize_spatial_optimization()
        
        # Performance tracking
        self.fps = 60
        self.frame_count = 0
        self.last_fps_update = 0
        
        # Game state
        self.game_mode = self.settings.MODE_CAMPAIGN
        self.game_time = 0
        self.day_night_cycle = 0  # 0-1, 0=day, 1=night
        self.day_count = 1
        self.weather_state = "clear"
        self.weather_timer = 0
        
        # Combat
        self.combat_cooldown = 0
        self.player_mana = 100
        self.player_max_mana = 100
        self.mana_regen_rate = 5.0  # mana per second
        self.spell_cooldowns = {}
        self.special_abilities = {
            'dash': {'cooldown': 0, 'max_cooldown': 3.0},
            'shield': {'cooldown': 0, 'max_cooldown': 10.0},
            'rage': {'cooldown': 0, 'max_cooldown': 15.0}
        }
        self.player_gold = 0
        self.player_skills = {
            'combat': 1, 'crafting': 1, 'exploration': 1, 'survival': 1
        }
        self.achievements = set()
        self.stats = {
            'enemies_killed': 0,
            'items_collected': 0,
            'areas_explored': 0,
            'items_crafted': 0,
            'damage_dealt': 0,
            'damage_taken': 0,
            'time_played': 0
        }
        
        # UI state
        self.show_inventory = False
        self.show_quest_log = False
        self.show_crafting_menu = False
        self.show_map = False
        self.show_settings_menu = False
        self.show_save_menu = False
        self.show_skill_tree = False
        self.show_achievements = False
        self.show_trading_menu = False
        
        # Message system
        self.messages = []
        self.message_timer = 0
        
        # Initialize quests
        # QuestSystem initializes its own quests in _initialize_quests()
        
        # Initialize crafting recipes
        # CraftingSystem initializes its own recipes in _initialize_recipes()
        
        # Set initial ambient light
        self.renderer.set_ambient_light(0.8)
    
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
        
        # Add player light source
        self.renderer.add_light_source(self.player.x, self.player.y, "player")
        
        # Set initial ambient light
        self.renderer.set_ambient_light(0.8)  # Start with bright lighting
    
    def exit(self):
        """Called when exiting game state"""
        self.logger.info("Exiting game state")
        self.sound_manager.stop_music()
    
    def handle_event(self, event):
        """Handle pygame events"""
        # Track key states
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            self.keys_just_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            self.keys_just_released.add(event.key)
        
        # Check UI menus first
        if self.show_quest_log:
            if self._handle_quest_log_event(event):
                return
        elif self.show_crafting_menu:
            if self._handle_crafting_menu_event(event):
                return
        elif self.show_settings_menu:
            if self._handle_settings_menu_event(event):
                return
        elif self.show_map:
            if self._handle_map_event(event):
                return
        elif self.show_save_menu:
            if self._handle_save_menu_event(event):
                return
        elif self.show_skill_tree:
            if self._handle_skill_tree_event(event):
                return
        elif self.show_achievements:
            if self._handle_achievements_event(event):
                return
        elif self.show_trading_menu:
            if self._handle_trading_menu_event(event):
                return
        
        # Handle game events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_engine.change_state("pause")
                return
            
            # Menu toggles
            elif event.key == pygame.K_i:
                self._toggle_inventory()
            elif event.key == pygame.K_q:
                self._toggle_quest_log()
            elif event.key == pygame.K_c:
                self._toggle_crafting_menu()
            elif event.key == pygame.K_m:
                self._toggle_map()
            elif event.key == pygame.K_s:
                self._toggle_settings_menu()
            elif event.key == pygame.K_l:
                self._toggle_save_menu()
            elif event.key == pygame.K_k:
                self._toggle_skill_tree()
            elif event.key == pygame.K_a:
                self._toggle_achievements()
            elif event.key == pygame.K_b:
                self._toggle_trading_menu()
            
            # Combat
            elif event.key == pygame.K_SPACE:
                self._attack_nearest_enemy()
            elif event.key == pygame.K_e:
                self._pickup_nearby_items()
            
            # Items
            elif event.key == pygame.K_1:
                self._use_health_potion()
            elif event.key == pygame.K_2:
                self._use_mana_potion()
            elif event.key == pygame.K_3:
                self._use_strength_potion()
            
            # Magic
            elif event.key == pygame.K_f:
                self._cast_fireball()
            elif event.key == pygame.K_g:
                self._cast_ice_bolt()
            elif event.key == pygame.K_h:
                self._cast_lightning()
            elif event.key == pygame.K_j:
                self._cast_heal()
            
            # Special abilities
            elif event.key == pygame.K_TAB:
                self._use_dash()
            elif event.key == pygame.K_r:
                self._use_shield()
            elif event.key == pygame.K_t:
                self._use_rage()
            
            # Save/Load
            elif event.key == pygame.K_F5:
                self._save_game(1)
            elif event.key == pygame.K_F9:
                self._load_game(1)
    
    def update(self, dt):
        """Update game state"""
        # Update performance tracking
        self._update_performance_tracking(dt)
        
        # Update camera
        self._update_camera(dt)
        
        # Update player input
        self._update_player_input(dt)
        
        # Update enemies
        self._update_enemies(dt)
        
        # Spawn enemies periodically
        self._spawn_enemies_periodically(dt)
        
        # Update quest progress
        self._update_quest_progress()
        
        # Update magic and abilities
        self._update_magic_and_abilities(dt)
        
        # Update weather and time
        self._update_weather_and_time(dt)
        
        # Check achievements
        self._check_achievements()
        
        # Update combat cooldown
        if self.combat_cooldown > 0:
            self.combat_cooldown -= dt
    
    def _update_player_input(self, dt):
        """Update player input handling"""
        # Get current key states
        keys = pygame.key.get_pressed()
        
        # Movement
        dx = 0
        dy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/sqrt(2)
            dy *= 0.707
        
        # Update player movement
        if dx != 0 or dy != 0:
            self.player.move(dx * self.player.speed * dt, dy * self.player.speed * dt)
        
        if not any([keys[pygame.K_w], keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d]]):
            pass # No keys detected - window may not have focus
    
    def render(self, screen):
        """Render the game with advanced graphics"""
        # Debug: Fill screen with a visible color first
        screen.fill((50, 100, 150))  # Blue background for debugging
        
        # Debug output
        # print(f"Rendering game state - Player at ({self.player.x:.0f}, {self.player.y:.0f})")
        # print(f"Camera at ({self.camera_x:.0f}, {self.camera_y:.0f})")
        # print(f"Enemies: {len(self.enemies)}")
        
        # Render world directly to screen (bypass lighting for now)
        self.world_generator.render_world(screen, (self.camera_x, self.camera_y))
        
        # Debug: Ensure world is visible by adding test rectangles
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 100, 100))  # Red test rectangle
        pygame.draw.rect(screen, (0, 255, 0), (120, 10, 100, 100))  # Green test rectangle
        pygame.draw.rect(screen, (255, 255, 0), (230, 10, 100, 100))  # Yellow test rectangle
        
        # Render player as a simple rectangle
        player_screen_x = self.player.x - self.camera_x
        player_screen_y = self.player.y - self.camera_y
        pygame.draw.rect(screen, (255, 255, 255), (player_screen_x - 24, player_screen_y - 24, 48, 48))
        
        # Render enemies using their sprites
        for enemy in self.enemies:
            if enemy.alive:
                enemy.render(screen, (self.camera_x, self.camera_y))
        
        # Render UI
        self._render_ui(screen)
        
        # Render weather effects
        self._render_weather_effects(screen)
        
        # Render menus
        if self.show_quest_log:
            self._render_quest_log(screen)
        elif self.show_crafting_menu:
            self._render_crafting_menu(screen)
        elif self.show_settings_menu:
            self._render_settings_menu(screen)
        elif self.show_map:
            self._render_map(screen)
        elif self.show_save_menu:
            self._render_save_menu(screen)
        elif self.show_skill_tree:
            self._render_skill_tree(screen)
        elif self.show_achievements:
            self._render_achievements(screen)
        elif self.show_trading_menu:
            self._render_trading_menu(screen)
        
        # Apply post-processing
        self.renderer.apply_post_processing(screen)
        
        # Render fade overlay
        self.renderer.render_fade_overlay(screen)
    
    def _render_ui(self, screen):
        """Render the game UI"""
        # Prepare player data for UI
        player_data = {
            'health': self.player.health,
            'max_health': self.player.max_health,
            'experience': self.player.experience,
            'experience_to_next': self.player.experience_to_next_level,
            'level': self.player.level,
            'attack': self.player.attack_power,
            'defense': self.player.defense,
            'speed': self.player.speed,
            'mana': self.player_mana,
            'max_mana': self.player_max_mana
        }
        
        # Prepare game data for UI
        game_data = {
            'player_pos': (self.player.x, self.player.y),
            'world_width': self.world_generator.world_width,
            'world_height': self.world_generator.world_height
        }
        
        # Render HUD using UI system
        self.ui_system.render_game_hud(screen, player_data, game_data)
        
        # Render inventory
        self.inventory_ui.render(screen, self.player)
        
        # Render messages
        self._render_messages(screen)
        
        # Render debug info
        if self.settings.DEBUG_MODE:
            self._render_debug_info(screen)
        
        # Render time and weather
        self._render_time_display(screen)
    
    def _render_messages(self, screen):
        """Render message log"""
        if not self.messages:
            return
        
        font = pygame.font.Font(None, 18)
        y_offset = 10
        
        for i, message in enumerate(self.messages[-3:]):  # Show last 3 messages
            text_surface = font.render(message, True, (255, 255, 255))
            screen.blit(text_surface, (10, screen.get_height() - 150 + y_offset))
            y_offset += 25
    
    def _render_debug_info(self, screen):
        """Render debug information"""
        font = pygame.font.Font(None, 16)
        
        debug_info = [
            f"FPS: {self.current_fps:.1f}",
            f"Entities: {len(self.enemies)}",
            f"Particles: {len(self.particle_system.particles)}",
            f"Camera: ({self.camera_x:.0f}, {self.camera_y:.0f})",
            f"Player: ({self.player.x:.0f}, {self.player.y:.0f})",
            f"Lights: {len(self.renderer.light_sources)}"
        ]
        
        for i, info in enumerate(debug_info):
            text = font.render(info, True, (255, 255, 255))
            screen.blit(text, (10, 200 + i * 15))
    
    def _update_performance_tracking(self, dt):
        """Update FPS and performance tracking"""
        self.frame_count += 1
        self.last_fps_update += dt
        
        if self.last_fps_update >= 1.0:
            self.fps = self.frame_count / self.last_fps_update
            self.frame_count = 0
            self.last_fps_update = 0
    
    def _update_camera(self, dt):
        """Update camera to follow player"""
        target_x = self.player.x - self.settings.SCREEN_WIDTH // 2
        target_y = self.player.y - self.settings.SCREEN_HEIGHT // 2
        
        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # Clamp camera to world bounds
        self.camera_x = max(0, min(self.camera_x, self.world_generator.world_width - self.settings.SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.world_generator.world_height - self.settings.SCREEN_HEIGHT))
        
        # Debug: Print camera position
        # print(f"Camera: ({self.camera_x:.0f}, {self.camera_y:.0f}) -> Target: ({target_x:.0f}, {target_y:.0f})")
    
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
                    
                    # Track damage taken
                    damage_taken = enemy.attack_power - self.player.defense
                    if damage_taken > 0:
                        self.stats['damage_taken'] += damage_taken
    
    def _spawn_enemy(self):
        """Spawn a basic enemy"""
        # Spawn enemy near the player (within 200-400 pixels)
        spawn_distance = random.uniform(200, 400)
        spawn_angle = random.uniform(0, 2 * math.pi)
        
        x = self.player.x + spawn_distance * math.cos(spawn_angle)
        y = self.player.y + spawn_distance * math.sin(spawn_angle)
        
        # Keep within world bounds
        x = max(0, min(x, self.world_generator.world_width))
        y = max(0, min(y, self.world_generator.world_height))
        
        enemy = Enemy(x, y, self.settings)
        
        # Give enemy patrol points around spawn location
        patrol_radius = 100
        patrol_points = [
            (x + patrol_radius, y),
            (x, y + patrol_radius),
            (x - patrol_radius, y),
            (x, y - patrol_radius)
        ]
        enemy.set_patrol_points(patrol_points)
        
        self.enemies.append(enemy)
        self.render_optimizer.add_entity(enemy)
        print(f"Spawned enemy at ({x:.0f}, {y:.0f}) - Player at ({self.player.x:.0f}, {self.player.y:.0f})")
    
    def _spawn_elite_enemy(self):
        """Spawn an elite enemy"""
        from game.entities.advanced_enemies import EliteEnemy
        
        # Spawn enemy near the player (within 300-500 pixels)
        spawn_distance = random.uniform(300, 500)
        spawn_angle = random.uniform(0, 2 * math.pi)
        
        x = self.player.x + spawn_distance * math.cos(spawn_angle)
        y = self.player.y + spawn_distance * math.sin(spawn_angle)
        
        # Keep within world bounds
        x = max(0, min(x, self.world_generator.world_width))
        y = max(0, min(y, self.world_generator.world_height))
        
        enemy_types = ["warrior", "archer", "mage", "assassin"]
        enemy_type = random.choice(enemy_types)
        enemy = EliteEnemy(x, y, self.settings, enemy_type)
        
        # Give elite enemy patrol points
        patrol_radius = 150
        patrol_points = [
            (x + patrol_radius, y),
            (x, y + patrol_radius),
            (x - patrol_radius, y),
            (x, y - patrol_radius)
        ]
        enemy.set_patrol_points(patrol_points)
        
        self.enemies.append(enemy)
        self.render_optimizer.add_entity(enemy)
        self._add_message(f"Elite {enemy_type.title()} appeared!")
        print(f"Spawned elite enemy at ({x:.0f}, {y:.0f}) - Player at ({self.player.x:.0f}, {self.player.y:.0f})")
    
    def _spawn_boss(self):
        """Spawn a boss enemy"""
        from game.entities.advanced_enemies import BossEnemy
        x = random.randint(0, self.world_generator.world_width)
        y = random.randint(0, self.world_generator.world_height)
        boss_types = ["dragon", "lich", "golem"]
        boss_type = random.choice(boss_types)
        boss = BossEnemy(x, y, self.settings, boss_type)
        
        # Give boss patrol points
        patrol_radius = 200
        patrol_points = [
            (x + patrol_radius, y),
            (x, y + patrol_radius),
            (x - patrol_radius, y),
            (x, y - patrol_radius)
        ]
        boss.set_patrol_points(patrol_points)
        
        self.enemies.append(boss)
        self.render_optimizer.add_entity(boss)
        self._add_message(f"BOSS {boss_type.upper()} has appeared!")
        self.sound_manager.play_combat_sounds("boss_spawn")
    
    def _spawn_enemies_periodically(self, dt):
        """Spawn enemies periodically"""
        # Spawn basic enemies
        if len(self.enemies) < 15 and random.random() < 0.02:  # 2% chance per frame
            self._spawn_enemy()
        
        # Spawn elite enemies occasionally
        if len(self.enemies) < 10 and random.random() < 0.01:  # 1% chance per frame
            self._spawn_elite_enemy()
        
        # Spawn bosses rarely
        if len(self.enemies) < 5 and random.random() < 0.002:  # 0.2% chance per frame
            self._spawn_boss()
    
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
            print(f"Attacking enemy at distance {nearest_distance:.1f}")
            attack_success = self.player.attack(nearest_enemy)
            
            if attack_success:
                self.combat_cooldown = 0.2
                self._add_message(f"Attacked {nearest_enemy.enemy_type}!")
                self.sound_manager.play_combat_sounds("attack")
                
                # Create combat effect
                self.particle_system.create_combat_effect(nearest_enemy.x, nearest_enemy.y, "slash")
                
                # Apply screen shake
                self.renderer.apply_screen_shake(2.0)
                
                # Check if enemy died
                if not nearest_enemy.alive:
                    self.score += 10
                    self.player.gain_experience(20)
                    self._add_message(f"Defeated {nearest_enemy.enemy_type}! +20 XP")
                    self.sound_manager.play_combat_sounds("enemy_death")
                    self.stats['enemies_killed'] += 1
        else:
            print("No enemies in range")
    
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
                    self.stats['items_collected'] += 1
                else:
                    self._add_message("Inventory full!")
        
        # Remove picked up items
        for item_data in items_to_remove:
            self.items.remove(item_data)
    
    def _cast_fireball(self):
        """Cast fireball spell"""
        if self.player_mana >= 20 and self.spell_cooldowns.get('fireball', 0) <= 0:
            self.player_mana -= 20
            self.spell_cooldowns['fireball'] = 2.0
            
            # Find nearest enemy
            nearest_enemy = None
            nearest_distance = float('inf')
            
            for enemy in self.enemies:
                distance = ((self.player.x - enemy.x) ** 2 + (self.player.y - enemy.y) ** 2) ** 0.5
                if distance < nearest_distance and distance <= 200:
                    nearest_distance = distance
                    nearest_enemy = enemy
            
            if nearest_enemy:
                damage = 30
                nearest_enemy.health -= damage
                self.stats['damage_dealt'] += damage
                
                self.particle_system.create_combat_effect(nearest_enemy.x, nearest_enemy.y, "fireball")
                self.sound_manager.play_combat_sounds("attack")
                self._add_message(f"Fireball hit enemy for {damage} damage!")
            else:
                self._add_message("No enemies in range for fireball!")
        elif self.player_mana < 20:
            self._add_message("Not enough mana for fireball!")
        else:
            self._add_message("Fireball is on cooldown!")
    
    def _cast_ice_bolt(self):
        """Cast ice bolt spell"""
        if self.player_mana >= 15 and self.spell_cooldowns.get('ice_bolt', 0) <= 0:
            self.player_mana -= 15
            self.spell_cooldowns['ice_bolt'] = 1.5
            
            nearest_enemy = None
            nearest_distance = float('inf')
            
            for enemy in self.enemies:
                distance = ((self.player.x - enemy.x) ** 2 + (self.player.y - enemy.y) ** 2) ** 0.5
                if distance < nearest_distance and distance <= 150:
                    nearest_distance = distance
                    nearest_enemy = enemy
            
            if nearest_enemy:
                damage = 20
                nearest_enemy.health -= damage
                self.stats['damage_dealt'] += damage
                
                self.particle_system.create_combat_effect(nearest_enemy.x, nearest_enemy.y, "ice")
                self.sound_manager.play_combat_sounds("attack")
                self._add_message(f"Ice bolt hit enemy for {damage} damage!")
            else:
                self._add_message("No enemies in range for ice bolt!")
        elif self.player_mana < 15:
            self._add_message("Not enough mana for ice bolt!")
        else:
            self._add_message("Ice bolt is on cooldown!")
    
    def _cast_lightning(self):
        """Cast lightning spell"""
        if self.player_mana >= 25 and self.spell_cooldowns.get('lightning', 0) <= 0:
            self.player_mana -= 25
            self.spell_cooldowns['lightning'] = 3.0
            
            enemies_hit = 0
            total_damage = 0
            
            for enemy in self.enemies:
                distance = ((self.player.x - enemy.x) ** 2 + (self.player.y - enemy.y) ** 2) ** 0.5
                if distance <= 120:
                    damage = 25
                    enemy.health -= damage
                    total_damage += damage
                    enemies_hit += 1
                    self.particle_system.create_combat_effect(enemy.x, enemy.y, "lightning")
            
            if enemies_hit > 0:
                self.stats['damage_dealt'] += total_damage
                self.sound_manager.play_combat_sounds("attack")
                self._add_message(f"Lightning hit {enemies_hit} enemies for {total_damage} total damage!")
            else:
                self._add_message("No enemies in range for lightning!")
        elif self.player_mana < 25:
            self._add_message("Not enough mana for lightning!")
        else:
            self._add_message("Lightning is on cooldown!")
    
    def _cast_heal(self):
        """Cast heal spell"""
        if self.player_mana >= 30 and self.spell_cooldowns.get('heal', 0) <= 0:
            self.player_mana -= 30
            self.spell_cooldowns['heal'] = 5.0
            
            heal_amount = 40
            self.player.health = min(self.player.max_health, self.player.health + heal_amount)
            
            self.particle_system.create_heal_effect(self.player.x, self.player.y, heal_amount)
            self.sound_manager.play_combat_sounds("heal")
            self._add_message(f"Heal spell restored {heal_amount} health!")
        elif self.player_mana < 30:
            self._add_message("Not enough mana for heal!")
        else:
            self._add_message("Heal is on cooldown!")
    
    def _use_dash(self):
        """Use dash ability"""
        if self.special_abilities['dash']['cooldown'] <= 0:
            self.special_abilities['dash']['cooldown'] = self.special_abilities['dash']['max_cooldown']
            
            # Move player in facing direction
            import math
            dash_distance = 100
            self.player.x += math.cos(self.player.facing_angle) * dash_distance
            self.player.y += math.sin(self.player.facing_angle) * dash_distance
            
            self.particle_system.create_combat_effect(self.player.x, self.player.y, "dash")
            self.sound_manager.play_combat_sounds("attack")
            self._add_message("Dashed forward!")
        else:
            cooldown_remaining = self.special_abilities['dash']['cooldown']
            self._add_message(f"Dash is on cooldown! ({cooldown_remaining:.1f}s)")
    
    def _use_shield(self):
        """Use shield ability"""
        if self.special_abilities['shield']['cooldown'] <= 0:
            self.special_abilities['shield']['cooldown'] = self.special_abilities['shield']['max_cooldown']
            
            # Temporarily increase defense
            original_defense = getattr(self.player, 'defense', 10)
            self.player.defense = original_defense * 2
            
            self.particle_system.create_heal_effect(self.player.x, self.player.y, 0)
            self.sound_manager.play_combat_sounds("heal")
            self._add_message("Shield activated! Defense doubled!")
            
            # Reset defense after 5 seconds
            import threading
            def reset_defense():
                import time
                time.sleep(5)
                self.player.defense = original_defense
                self._add_message("Shield deactivated.")
            
            threading.Thread(target=reset_defense, daemon=True).start()
        else:
            cooldown_remaining = self.special_abilities['shield']['cooldown']
            self._add_message(f"Shield is on cooldown! ({cooldown_remaining:.1f}s)")
    
    def _use_rage(self):
        """Use rage ability"""
        if self.special_abilities['rage']['cooldown'] <= 0:
            self.special_abilities['rage']['cooldown'] = self.special_abilities['rage']['max_cooldown']
            
            # Temporarily increase attack power
            original_attack = getattr(self.player, 'attack_power', 20)
            self.player.attack_power = original_attack * 2
            
            self.particle_system.create_combat_effect(self.player.x, self.player.y, "rage")
            self.sound_manager.play_combat_sounds("attack")
            self._add_message("Rage activated! Attack power doubled!")
            
            # Reset attack power after 10 seconds
            import threading
            def reset_attack():
                import time
                time.sleep(10)
                self.player.attack_power = original_attack
                self._add_message("Rage deactivated.")
            
            threading.Thread(target=reset_attack, daemon=True).start()
        else:
            cooldown_remaining = self.special_abilities['rage']['cooldown']
            self._add_message(f"Rage is on cooldown! ({cooldown_remaining:.1f}s)")
    
    def _use_health_potion(self):
        """Use health potion"""
        # Find health potion in inventory
        for item in self.player.inventory[:]:
            if item.name == "Health Potion":
                self.player.inventory.remove(item)
                heal_amount = 50
                self.player.health = min(self.player.max_health, self.player.health + heal_amount)
                self.particle_system.create_heal_effect(self.player.x, self.player.y, heal_amount)
                self.sound_manager.play_combat_sounds("heal")
                self._add_message(f"Used Health Potion! Restored {heal_amount} health!")
                return
        self._add_message("No Health Potion in inventory!")
    
    def _use_mana_potion(self):
        """Use mana potion"""
        for item in self.player.inventory[:]:
            if item.name == "Magic Potion":
                self.player.inventory.remove(item)
                mana_amount = 50
                self.player_mana = min(self.player_max_mana, self.player_mana + mana_amount)
                self.particle_system.create_heal_effect(self.player.x, self.player.y, mana_amount)
                self.sound_manager.play_combat_sounds("heal")
                self._add_message(f"Used Magic Potion! Restored {mana_amount} mana!")
                return
        self._add_message("No Magic Potion in inventory!")
    
    def _use_strength_potion(self):
        """Use strength potion"""
        for item in self.player.inventory[:]:
            if item.name == "Strength Potion":
                self.player.inventory.remove(item)
                # Temporarily increase attack power
                original_attack = getattr(self.player, 'attack_power', 20)
                self.player.attack_power = original_attack * 1.5
                
                self.particle_system.create_heal_effect(self.player.x, self.player.y, 0)
                self.sound_manager.play_combat_sounds("heal")
                self._add_message("Used Strength Potion! Attack power increased!")
                
                # Reset after 30 seconds
                import threading
                def reset_attack():
                    import time
                    time.sleep(30)
                    self.player.attack_power = original_attack
                    self._add_message("Strength potion effect wore off.")
                
                threading.Thread(target=reset_attack, daemon=True).start()
                return
        self._add_message("No Strength Potion in inventory!")
    
    def _toggle_quest_log(self):
        """Toggle quest log visibility"""
        self.show_quest_log = not self.show_quest_log
        if self.show_quest_log:
            self._add_message("Quest Log: Press Q to view active quests")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_crafting_menu(self):
        """Toggle crafting menu visibility"""
        self.show_crafting_menu = not self.show_crafting_menu
        if self.show_crafting_menu:
            self._add_message("Crafting: Press C to open crafting menu")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_map(self):
        """Toggle map visibility"""
        self.show_map = not self.show_map
        if self.show_map:
            self._add_message("Map: Press M to view world map")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_settings_menu(self):
        """Toggle settings menu visibility"""
        self.show_settings_menu = not self.show_settings_menu
        if self.show_settings_menu:
            self._add_message("Settings: Press S to open settings")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_save_menu(self):
        """Toggle save menu visibility"""
        self.show_save_menu = not self.show_save_menu
        if self.show_save_menu:
            self._add_message("Save Menu: Press L to save/load games")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_skill_tree(self):
        """Toggle skill tree visibility"""
        self.show_skill_tree = not self.show_skill_tree
        if self.show_skill_tree:
            self._add_message("Skill Tree: Press K to view skills")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_achievements(self):
        """Toggle achievements visibility"""
        self.show_achievements = not self.show_achievements
        if self.show_achievements:
            self._add_message("Achievements: Press A to view achievements")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_statistics(self):
        """Toggle statistics visibility"""
        self._add_message("Statistics: Press V to view stats")
        self.sound_manager.play_ui_sounds("select")
        # TODO: Implement statistics menu
    
    def _toggle_trading_menu(self):
        """Toggle trading menu visibility"""
        self.show_trading_menu = not self.show_trading_menu
        if self.show_trading_menu:
            self._add_message("Trading: Press B to open trading menu")
        self.sound_manager.play_ui_sounds("select")
    
    def _handle_quest_log_event(self, event):
        """Handle quest log events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                self.show_quest_log = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_crafting_menu_event(self, event):
        """Handle crafting menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c or event.key == pygame.K_ESCAPE:
                self.show_crafting_menu = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_settings_menu_event(self, event):
        """Handle settings menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s or event.key == pygame.K_ESCAPE:
                self.show_settings_menu = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_map_event(self, event):
        """Handle map events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                self.show_map = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_save_menu_event(self, event):
        """Handle save menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l or event.key == pygame.K_ESCAPE:
                self.show_save_menu = False
                self.sound_manager.play_ui_sounds("select")
                return True
            elif event.key == pygame.K_1:
                self._save_game(1)
                return True
            elif event.key == pygame.K_2:
                self._save_game(2)
                return True
            elif event.key == pygame.K_3:
                self._save_game(3)
                return True
            elif event.key == pygame.K_4:
                self._load_game(1)
                return True
            elif event.key == pygame.K_5:
                self._load_game(2)
                return True
            elif event.key == pygame.K_6:
                self._load_game(3)
                return True
        return False
    
    def _handle_skill_tree_event(self, event):
        """Handle skill tree events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k or event.key == pygame.K_ESCAPE:
                self.show_skill_tree = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_achievements_event(self, event):
        """Handle achievements events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_ESCAPE:
                self.show_achievements = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_trading_menu_event(self, event):
        """Handle trading menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b or event.key == pygame.K_ESCAPE:
                self.show_trading_menu = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _render_quest_log(self, screen):
        """Render quest log"""
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Quest log panel
        panel_width, panel_height = 600, 400
        x = (screen.get_width() - panel_width) // 2
        y = (screen.get_height() - panel_height) // 2
        
        # Panel background
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 50, 80, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel, (100, 100, 150), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (x, y))
        
        # Title
        font = pygame.font.Font(None, 36)
        title_text = font.render("Quest Log", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(x + panel_width // 2, y + 30))
        screen.blit(title_text, title_rect)
        
        # Quest information
        quest_summary = self.quest_system.get_quest_summary()
        font_small = pygame.font.Font(None, 20)
        
        info_lines = [
            f"Active Quests: {quest_summary['active']}",
            f"Completed Quests: {quest_summary['completed']}",
            f"Available Quests: {quest_summary['available']}",
            f"Enemies Killed: {quest_summary['total_enemies_killed']}",
            f"Items Collected: {quest_summary['total_items_collected']}",
            f"Areas Explored: {quest_summary['total_areas_explored']}"
        ]
        
        for i, line in enumerate(info_lines):
            text = font_small.render(line, True, (255, 255, 255))
            screen.blit(text, (x + 20, y + 80 + i * 30))
        
        # Instructions
        instructions = [
            "Press Q or ESC to close",
            "Complete quests to earn rewards!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            screen.blit(text, (x + 20, y + panel_height - 60 + i * 25))
    
    def _render_crafting_menu(self, screen):
        """Render crafting menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Crafting menu panel
        panel_width, panel_height = 700, 500
        x = (screen.get_width() - panel_width) // 2
        y = (screen.get_height() - panel_height) // 2
        
        # Panel background
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 50, 80, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel, (100, 100, 150), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (x, y))
        
        # Title
        font = pygame.font.Font(None, 36)
        title_text = font.render("Crafting Menu", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(x + panel_width // 2, y + 30))
        screen.blit(title_text, title_rect)
        
        # Get available recipes
        available_recipes = self.crafting_system.get_available_recipes(self.player.inventory, self.player.level)
        
        # Display recipes
        font_small = pygame.font.Font(None, 18)
        recipe_y = y + 80
        
        if available_recipes:
            for i, recipe in enumerate(available_recipes[:10]):  # Show first 10 recipes
                recipe_text = f"{recipe.name} - {recipe.description}"
                text = font_small.render(recipe_text, True, (255, 255, 255))
                screen.blit(text, (x + 20, recipe_y + i * 25))
        else:
            no_recipes_text = "No recipes available. Collect materials to unlock recipes!"
            text = font_small.render(no_recipes_text, True, (200, 200, 200))
            screen.blit(text, (x + 20, recipe_y))
        
        # Instructions
        instructions = [
            "Press C or ESC to close",
            "Collect materials to craft items!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            screen.blit(text, (x + 20, y + panel_height - 60 + i * 25))
    
    def _render_settings_menu(self, screen):
        """Render settings menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Settings panel
        panel_width, panel_height = 400, 300
        x = (screen.get_width() - panel_width) // 2
        y = (screen.get_height() - panel_height) // 2
        
        # Panel background
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 50, 80, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel, (100, 100, 150), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (x, y))
        
        # Title
        font = pygame.font.Font(None, 36)
        title_text = font.render("Settings", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(x + panel_width // 2, y + 30))
        screen.blit(title_text, title_rect)
        
        # Settings options
        font_small = pygame.font.Font(None, 20)
        settings = [
            "Sound Effects: ON",
            "Music: ON",
            "Debug Mode: OFF",
            "Fullscreen: OFF"
        ]
        
        for i, setting in enumerate(settings):
            text = font_small.render(setting, True, (255, 255, 255))
            screen.blit(text, (x + 20, y + 80 + i * 30))
        
        # Instructions
        instructions = [
            "Press S or ESC to close",
            "Settings coming soon!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            screen.blit(text, (x + 20, y + panel_height - 60 + i * 25))
    
    def _render_map(self, screen):
        """Render world map"""
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Map panel
        panel_width, panel_height = 600, 400
        x = (screen.get_width() - panel_width) // 2
        y = (screen.get_height() - panel_height) // 2
        
        # Panel background
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 50, 80, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel, (100, 100, 150), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (x, y))
        
        # Title
        font = pygame.font.Font(None, 36)
        title_text = font.render("World Map", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(x + panel_width // 2, y + 30))
        screen.blit(title_text, title_rect)
        
        # Map content
        map_surface = pygame.Surface((panel_width - 40, panel_height - 100))
        map_surface.fill((30, 30, 50))
        
        # Draw simplified world representation
        for i in range(0, panel_width - 40, 10):
            for j in range(0, panel_height - 100, 10):
                # Create a simple pattern
                if (i + j) % 20 == 0:
                    pygame.draw.rect(map_surface, (60, 60, 80), (i, j, 8, 8))
        
        # Draw player position
        player_x = int((self.player.x / self.world_generator.world_width) * (panel_width - 40))
        player_y = int((self.player.y / self.world_generator.world_height) * (panel_height - 100))
        pygame.draw.circle(map_surface, (100, 200, 255), (player_x, player_y), 5)
        
        screen.blit(map_surface, (x + 20, y + 80))
        
        # Instructions
        font_small = pygame.font.Font(None, 20)
        instructions = [
            "Press M or ESC to close",
            "Explore the world to reveal more!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            screen.blit(text, (x + 20, y + panel_height - 60 + i * 25))
    
    def _render_save_menu(self, screen):
        """Render save menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Save menu panel
        panel_width, panel_height = 400, 300
        x = (screen.get_width() - panel_width) // 2
        y = (screen.get_height() - panel_height) // 2
        
        # Panel background
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 50, 80, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel, (100, 100, 150), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (x, y))
        
        # Title
        font = pygame.font.Font(None, 36)
        title_text = font.render("Save/Load Menu", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(x + panel_width // 2, y + 30))
        screen.blit(title_text, title_rect)
        
        # Save slots
        font_small = pygame.font.Font(None, 20)
        save_slots = [
            "Slot 1: " + ("Empty" if self.save_system.is_slot_empty(1) else "Game"),
            "Slot 2: " + ("Empty" if self.save_system.is_slot_empty(2) else "Game"),
            "Slot 3: " + ("Empty" if self.save_system.is_slot_empty(3) else "Game")
        ]
        
        for i, slot_info in enumerate(save_slots):
            text = font_small.render(slot_info, True, (255, 255, 255))
            screen.blit(text, (x + 20, y + 80 + i * 30))
        
        # Load slots
        load_slots = [
            "Slot 1: " + ("Empty" if self.save_system.is_slot_empty(1) else "Game"),
            "Slot 2: " + ("Empty" if self.save_system.is_slot_empty(2) else "Game"),
            "Slot 3: " + ("Empty" if self.save_system.is_slot_empty(3) else "Game")
        ]
        
        for i, slot_info in enumerate(load_slots):
            text = font_small.render(slot_info, True, (255, 255, 255))
            screen.blit(text, (x + 20, y + 140 + i * 30))
        
        # Instructions
        instructions = [
            "Press L or ESC to close",
            "Press 1-3 to save, 4-6 to load"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            screen.blit(text, (x + 20, y + panel_height - 60 + i * 25))
    
    def _render_skill_tree(self, screen):
        """Render skill tree"""
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Skill tree panel
        panel_width, panel_height = 600, 400
        x = (screen.get_width() - panel_width) // 2
        y = (screen.get_height() - panel_height) // 2
        
        # Panel background
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 50, 80, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel, (100, 100, 150), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (x, y))
        
        # Title
        font = pygame.font.Font(None, 36)
        title_text = font.render("Skill Tree", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(x + panel_width // 2, y + 30))
        screen.blit(title_text, title_rect)
        
        # Skill categories
        font_small = pygame.font.Font(None, 20)
        categories = [
            "Combat",
            "Crafting",
            "Exploration",
            "Survival"
        ]
        
        for i, category in enumerate(categories):
            text = font_small.render(category, True, (255, 255, 255))
            screen.blit(text, (x + 20, y + 80 + i * 30))
        
        # Skill points
        font_small = pygame.font.Font(None, 18)
        skill_points = [
            f"Combat: {self.player_skills['combat']}",
            f"Crafting: {self.player_skills['crafting']}",
            f"Exploration: {self.player_skills['exploration']}",
            f"Survival: {self.player_skills['survival']}"
        ]
        
        for i, points in enumerate(skill_points):
            text = font_small.render(points, True, (255, 255, 255))
            screen.blit(text, (x + 20, y + 140 + i * 30))
        
        # Instructions
        instructions = [
            "Press K or ESC to close",
            "Spend skill points to improve your abilities!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            screen.blit(text, (x + 20, y + panel_height - 60 + i * 25))
    
    def _render_achievements(self, screen):
        """Render achievements"""
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Achievements panel
        panel_width, panel_height = 600, 400
        x = (screen.get_width() - panel_width) // 2
        y = (screen.get_height() - panel_height) // 2
        
        # Panel background
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 50, 80, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel, (100, 100, 150), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (x, y))
        
        # Title
        font = pygame.font.Font(None, 36)
        title_text = font.render("Achievements", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(x + panel_width // 2, y + 30))
        screen.blit(title_text, title_rect)
        
        # Achievement list
        font_small = pygame.font.Font(None, 18)
        achievement_y = y + 80
        
        for achievement_name, achievement_data in self.achievements.items():
            if achievement_data['unlocked']:
                text_color = (255, 255, 255) # White for unlocked
            else:
                text_color = (150, 150, 150) # Gray for locked
            
            achievement_text = f"{achievement_data['name']} - {achievement_data['description']}"
            text = font_small.render(achievement_text, True, text_color)
            screen.blit(text, (x + 20, achievement_y))
            achievement_y += 25
        
        # Instructions
        instructions = [
            "Press A or ESC to close",
            "Earn achievements to unlock new abilities!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            screen.blit(text, (x + 20, y + panel_height - 60 + i * 25))
    
    def _render_trading_menu(self, screen):
        """Render trading menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Trading menu panel
        panel_width, panel_height = 600, 400
        x = (screen.get_width() - panel_width) // 2
        y = (screen.get_height() - panel_height) // 2
        
        # Panel background
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 50, 80, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel, (100, 100, 150), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel, (x, y))
        
        # Title
        font = pygame.font.Font(None, 36)
        title_text = font.render("Trading Menu", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(x + panel_width // 2, y + 30))
        screen.blit(title_text, title_rect)
        
        # Display player's inventory
        font_small = pygame.font.Font(None, 18)
        inventory_y = y + 80
        
        if self.player.inventory:
            for i, item in enumerate(self.player.inventory):
                item_text = f"{item.name} (x{self.player.get_item_count(item.name)})"
                text = font_small.render(item_text, True, (255, 255, 255))
                screen.blit(text, (x + 20, inventory_y + i * 25))
        else:
            no_items_text = "Your inventory is empty. Collect items to trade!"
            text = font_small.render(no_items_text, True, (200, 200, 200))
            screen.blit(text, (x + 20, inventory_y))
        
        # Display merchant's inventory
        merchant_inventory_y = y + 150
        
        if self.merchant_inventory:
            for i, item_data in enumerate(self.merchant_inventory):
                item_text = f"{item_data['item'].name} - Price: {item_data['price']} Gold"
                text = font_small.render(item_text, True, (255, 255, 255))
                screen.blit(text, (x + 20, merchant_inventory_y + i * 25))
        else:
            no_merchant_items_text = "The merchant has no items to sell."
            text = font_small.render(no_merchant_items_text, True, (200, 200, 200))
            screen.blit(text, (x + 20, merchant_inventory_y))
        
        # Instructions
        instructions = [
            "Press B or ESC to close",
            "Trade items with the merchant!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            screen.blit(text, (x + 20, y + panel_height - 60 + i * 25))
    
    def _render_weather_effects(self, screen):
        """Render weather effects overlay"""
        if self.weather_state == "rain":
            # Create rain effect
            for _ in range(50):
                x = random.randint(0, screen.get_width())
                y = random.randint(0, screen.get_height())
                pygame.draw.line(screen, (100, 150, 255), (x, y), (x, y + 10), 1)
        elif self.weather_state == "storm":
            # Create storm effect (more intense rain)
            for _ in range(100):
                x = random.randint(0, screen.get_width())
                y = random.randint(0, screen.get_height())
                pygame.draw.line(screen, (80, 120, 200), (x, y), (x, y + 15), 2)
        elif self.weather_state == "fog":
            # Create fog effect
            fog_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            fog_surface.fill((200, 200, 200, 50))
            screen.blit(fog_surface, (0, 0))
    
    def _render_time_display(self, screen):
        """Render time and weather display"""
        font = pygame.font.Font(None, 20)
        
        # Format time
        hours = int(self.day_night_cycle)
        minutes = int((self.day_night_cycle - hours) * 60)
        time_text = f"Day {self.day_count} - {hours:02d}:{minutes:02d}"
        
        # Weather text
        weather_text = f"Weather: {self.weather_state.title()}"
        
        # Render time
        time_surface = font.render(time_text, True, (255, 255, 255))
        screen.blit(time_surface, (screen.get_width() - 200, 10))
        
        # Render weather
        weather_surface = font.render(weather_text, True, (255, 255, 255))
        screen.blit(weather_surface, (screen.get_width() - 200, 35))
    
    def _update_quest_progress(self):
        """Update quest progress"""
        # Update kill quests
        if self.stats['enemies_killed'] > 0:
            self.quest_system.update_progress("kill", self.stats['enemies_killed'])
        
        # Update collect quests
        if self.stats['items_collected'] > 0:
            self.quest_system.update_progress("collect", self.stats['items_collected'])
        
        # Update explore quests
        if self.stats['areas_explored'] > 0:
            self.quest_system.update_progress("explore", self.stats['areas_explored'])
    
    def _update_magic_and_abilities(self, dt):
        """Update magic and ability cooldowns"""
        # Mana regeneration
        self.player_mana = min(self.player_max_mana, self.player_mana + self.mana_regen_rate * dt)
        
        # Update spell cooldowns
        for spell in self.spell_cooldowns:
            if self.spell_cooldowns[spell] > 0:
                self.spell_cooldowns[spell] -= dt
        
        # Update ability cooldowns
        for ability in self.special_abilities:
            if self.special_abilities[ability]['cooldown'] > 0:
                self.special_abilities[ability]['cooldown'] -= dt
    
    def _update_weather_and_time(self, dt):
        """Update weather and time system"""
        # Update weather timer
        self.weather_timer += dt
        
        # Change weather periodically
        if self.weather_timer >= 300:  # 5 minutes
            self.weather_timer = 0
            self.weather_state = random.choice(["clear", "rain", "storm", "fog"])
            
            if self.weather_state == "rain":
                self.sound_manager.play_ambient_sounds("rain")
            elif self.weather_state == "storm":
                self.sound_manager.play_ambient_sounds("storm")
            elif self.weather_state == "fog":
                self.sound_manager.play_ambient_sounds("fog")
        
        # Update day/night cycle
        self.day_night_cycle += dt / 60  # 1 second per minute
        if self.day_night_cycle >= 24:
            self.day_night_cycle = 0
            self._add_message("New day!")
    
    def _check_achievements(self):
        """Check and unlock achievements"""
        achievements_to_check = {
            'first_blood': self.stats['enemies_killed'] >= 1,
            'collector': self.stats['items_collected'] >= 10,
            'explorer': self.stats['areas_explored'] >= 5,
            'craftsman': self.stats['items_crafted'] >= 1,
            'survivor': self.player.level >= 5,
            'boss_slayer': any(isinstance(e, BossEnemy) for e in self.enemies if e.health <= 0)
        }
        
        for achievement, condition in achievements_to_check.items():
            if condition and achievement not in self.achievements:
                self.achievements.add(achievement)
                self._add_message(f"Achievement unlocked: {achievement.replace('_', ' ').title()}!")
                self.sound_manager.play_ui_sounds("achievement")
    
    def _save_game(self, slot):
        """Save game to slot"""
        from game.utils.save_system import SaveSystem
        save_system = SaveSystem()
        save_system.save_game(slot, self._get_game_state())
        self._add_message(f"Game saved to slot {slot}!")
    
    def _load_game(self, slot):
        """Load game from slot"""
        from game.utils.save_system import SaveSystem
        save_system = SaveSystem()
        game_state = save_system.load_game(slot)
        if game_state:
            self._set_game_state(game_state)
            self._add_message(f"Game loaded from slot {slot}!")
        else:
            self._add_message("No save file found in slot!")
    
    def _get_game_state(self):
        """Get current game state for saving"""
        return {
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'health': self.player.health,
                'max_health': self.player.max_health,
                'level': self.player.level,
                'experience': self.player.experience,
                'inventory': [item.name for item in self.player.inventory]
            },
            'game_time': self.game_time,
            'stats': self.stats,
            'achievements': list(self.achievements),
            'player_skills': self.player_skills,
            'day_night_cycle': self.day_night_cycle,
            'weather_state': self.weather_state,
            'player_mana': self.player_mana,
            'player_max_mana': self.player_max_mana,
            'player_gold': self.player_gold,
            'spell_cooldowns': self.spell_cooldowns,
            'special_abilities': self.special_abilities
        }
    
    def _set_game_state(self, game_state):
        """Set game state from loaded data"""
        if 'player' in game_state:
            player_data = game_state['player']
            self.player.x = player_data.get('x', 1000)
            self.player.y = player_data.get('y', 1000)
            self.player.health = player_data.get('health', 100)
            self.player.max_health = player_data.get('max_health', 100)
            self.player.level = player_data.get('level', 1)
            self.player.experience = player_data.get('experience', 0)
        
        self.game_time = game_state.get('game_time', 0)
        self.stats = game_state.get('stats', self.stats)
        self.achievements = set(game_state.get('achievements', []))
        self.player_skills = game_state.get('player_skills', self.player_skills)
        self.day_night_cycle = game_state.get('day_night_cycle', 0)
        self.weather_state = game_state.get('weather_state', "clear")
        self.player_mana = game_state.get('player_mana', 100)
        self.player_max_mana = game_state.get('player_max_mana', 100)
        self.player_gold = game_state.get('player_gold', 0)
        self.spell_cooldowns = game_state.get('spell_cooldowns', {})
        self.special_abilities = game_state.get('special_abilities', self.special_abilities)
    
    def _toggle_inventory(self):
        """Toggle inventory visibility"""
        self.show_inventory = not self.show_inventory
        if self.show_inventory:
            self._add_message("Inventory: Press I to view inventory")
        self.sound_manager.play_ui_sounds("select")
    
    def _add_message(self, message):
        """Add a message to the game log"""
        self.messages.append(message)
    
    def _game_over(self):
        """Handle game over"""
        self._add_message("Game Over! Press ESC to return to menu")
        self.sound_manager.play_ui_sounds("game_over")
        # For now, just return to menu after a delay
        import threading
        import time
        def delayed_return():
            time.sleep(3)
            self.game_engine.change_state("menu")
        threading.Thread(target=delayed_return, daemon=True).start()
