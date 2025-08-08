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
        self.ui_system = UISystem(self.settings)
        
        # Graphics and effects
        self.particle_system = ParticleSystem(self.settings)
        self.render_optimizer = RenderOptimizer(self.settings)
        self.renderer = Renderer(self.settings)
        
        # Audio system
        self.sound_manager = SoundManager(self.settings)
        
        # Game systems
        self.quest_system = QuestSystem(self.settings)
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
        
        # Game features
        self.quest_log_visible = False
        self.crafting_menu_visible = False
        self.map_visible = False
        self.settings_menu_visible = False
        self.save_menu_visible = False
        self.skill_tree_visible = False
        self.achievements_visible = False
        self.trading_menu_visible = False
        self.merchant_visible = False
        
        # Trading system
        self.merchant_inventory = [
            {'item': ItemFactory.create_item("Health Potion"), 'price': 10, 'quantity': 5},
            {'item': ItemFactory.create_item("Magic Potion"), 'price': 15, 'quantity': 3},
            {'item': ItemFactory.create_item("Strength Potion"), 'price': 20, 'quantity': 2},
            {'item': ItemFactory.create_item("Iron Sword"), 'price': 50, 'quantity': 1},
            {'item': ItemFactory.create_item("Leather Armor"), 'price': 30, 'quantity': 1}
        ]
        
        self.player_gold = 100
        
        # Magic system
        self.player_mana = 100
        self.player_max_mana = 100
        self.mana_regen_rate = 5  # mana per second
        self.spell_cooldowns = {
            'fireball': 0,
            'ice_bolt': 0,
            'lightning': 0,
            'heal': 0
        }
        
        # Special abilities
        self.special_abilities = {
            'dash': {'cooldown': 0, 'max_cooldown': 3.0},
            'shield': {'cooldown': 0, 'max_cooldown': 10.0},
            'rage': {'cooldown': 0, 'max_cooldown': 30.0}
        }
        
        # Weather and time system
        self.time_of_day = 0  # 0-24 hours
        self.day_count = 1
        self.weather = "clear"  # clear, rain, storm, fog
        self.weather_timer = 0
        self.weather_duration = random.uniform(300, 600)  # 5-10 minutes
        
        # Lighting based on time
        self.day_light_intensity = 1.0
        self.night_light_intensity = 0.3
        
        # Save system
        from game.utils.save_system import SaveSystem
        self.save_system = SaveSystem(self.settings)
        
        # Skill system
        self.player_skills = {
            'combat': 1,
            'crafting': 1,
            'exploration': 1,
            'survival': 1
        }
        
        # Achievement system
        self.achievements = {
            'first_blood': {'name': 'First Blood', 'description': 'Defeat your first enemy', 'unlocked': False},
            'collector': {'name': 'Collector', 'description': 'Collect 10 items', 'unlocked': False},
            'explorer': {'name': 'Explorer', 'description': 'Explore 5 different areas', 'unlocked': False},
            'craftsman': {'name': 'Craftsman', 'description': 'Craft your first item', 'unlocked': False},
            'survivor': {'name': 'Survivor', 'description': 'Reach level 5', 'unlocked': False},
            'boss_slayer': {'name': 'Boss Slayer', 'description': 'Defeat a boss enemy', 'unlocked': False}
        }
        
        # Statistics
        self.stats = {
            'enemies_killed': 0,
            'items_collected': 0,
            'areas_explored': 0,
            'items_crafted': 0,
            'damage_dealt': 0,
            'damage_taken': 0,
            'time_played': 0
        }
        
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
        
        # Add player light source
        self.renderer.add_light_source(self.player.x, self.player.y, "player")
    
    def exit(self):
        """Called when exiting game state"""
        self.logger.info("Exiting game state")
        self.sound_manager.stop_music()
    
    def handle_event(self, event):
        """Handle game events"""
        # Check UI menus first
        if self.quest_log_visible:
            if self._handle_quest_log_event(event):
                return
        elif self.crafting_menu_visible:
            if self._handle_crafting_menu_event(event):
                return
        elif self.settings_menu_visible:
            if self._handle_settings_menu_event(event):
                return
        elif self.map_visible:
            if self._handle_map_event(event):
                return
        elif self.save_menu_visible:
            if self._handle_save_menu_event(event):
                return
        elif self.skill_tree_visible:
            if self._handle_skill_tree_event(event):
                return
        elif self.achievements_visible:
            if self._handle_achievements_event(event):
                return
        elif self.trading_menu_visible:
            if self._handle_trading_menu_event(event):
                return
        
        # Check inventory
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
                self._toggle_map()
            elif event.key == pygame.K_q:
                self._toggle_quest_log()
            elif event.key == pygame.K_c:
                self._toggle_crafting_menu()
            elif event.key == pygame.K_f:
                self._use_health_potion()
            elif event.key == pygame.K_s:
                self._toggle_settings_menu()
            elif event.key == pygame.K_r:
                self._use_mana_potion()
            elif event.key == pygame.K_t:
                self._use_strength_potion()
            elif event.key == pygame.K_l:
                self._toggle_save_menu()
            elif event.key == pygame.K_k:
                self._toggle_skill_tree()
            elif event.key == pygame.K_a:
                self._toggle_achievements()
            elif event.key == pygame.K_v:
                self._toggle_statistics()
            elif event.key == pygame.K_b:
                self._toggle_trading_menu()
            elif event.key == pygame.K_z:
                self._cast_fireball()
            elif event.key == pygame.K_x:
                self._cast_ice_bolt()
            elif event.key == pygame.K_y:
                self._cast_lightning()
            elif event.key == pygame.K_h:
                self._cast_heal()
            elif event.key == pygame.K_d:
                self._use_dash()
            elif event.key == pygame.K_g:
                self._use_shield()
            elif event.key == pygame.K_u:
                self._use_rage()
        
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
        
        # Update lighting
        self.renderer.clear_lights()
        self.renderer.add_light_source(self.player.x, self.player.y, "player")
        
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
            self.stats['items_crafted'] += 1
        
        # Update statistics
        self.stats['time_played'] += dt
        
        # Check achievements
        self._check_achievements()
        
        # Update weather and time
        self._update_weather_and_time(dt)
        
        # Update magic and abilities
        self._update_magic_and_abilities(dt)
        
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
        """Render the game with advanced graphics"""
        # Create world surface
        world_surface = pygame.Surface(screen.get_size())
        world_surface.fill(self.settings.BLACK)
        
        # Render world
        self.world_generator.render_world(world_surface, (self.camera_x, self.camera_y))
        
        # Render visible enemies (optimized)
        visible_entities = self.render_optimizer.get_visible_entities()
        for enemy in self.enemies:
            if enemy.alive and enemy in visible_entities:
                enemy_sprite = self.renderer.sprite_sheet.get_sprite(enemy.enemy_type)
                if enemy_sprite:
                    self.renderer.render_entity_with_effects(world_surface, enemy_sprite,
                                                          enemy.x - self.camera_x,
                                                          enemy.y - self.camera_y,
                                                          "boss" if hasattr(enemy, 'is_boss') and enemy.is_boss else "enemy")
        
        # Render player
        player_sprite = self.renderer.sprite_sheet.get_sprite("player")
        if player_sprite:
            self.renderer.render_entity_with_effects(world_surface, player_sprite,
                                                  self.player.x - self.camera_x,
                                                  self.player.y - self.camera_y, "player")
        
        # Render particles
        self.particle_system.render(world_surface, (self.camera_x, self.camera_y))
        
        # Apply lighting
        self.renderer.render_world_with_lighting(screen, world_surface, (0, 0))
        
        # Render UI
        self._render_ui(screen)
        
        # Render weather effects
        self._render_weather_effects(screen)
        
        # Render menus
        if self.quest_log_visible:
            self._render_quest_log(screen)
        elif self.crafting_menu_visible:
            self._render_crafting_menu(screen)
        elif self.settings_menu_visible:
            self._render_settings_menu(screen)
        elif self.map_visible:
            self._render_map(screen)
        elif self.save_menu_visible:
            self._render_save_menu(screen)
        elif self.skill_tree_visible:
            self._render_skill_tree(screen)
        elif self.achievements_visible:
            self._render_achievements(screen)
        elif self.trading_menu_visible:
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
                    
                    # Track damage taken
                    damage_taken = enemy.attack_power - self.player.defense
                    if damage_taken > 0:
                        self.stats['damage_taken'] += damage_taken
    
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
                
                # Track damage dealt
                damage_dealt = self.player.attack_power - nearest_enemy.defense
                if damage_dealt > 0:
                    self.stats['damage_dealt'] += damage_dealt
                
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
                    self.stats['items_collected'] += 1
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
    
    def _use_mana_potion(self):
        """Use a mana potion"""
        mana_potion = None
        for item in self.player.inventory:
            if item.name == "Magic Potion":
                mana_potion = item
                break
        
        if mana_potion:
            self.player.inventory.remove(mana_potion)
            mana_amount = 100
            # TODO: Implement mana system
            self._add_message(f"Used Magic Potion! +{mana_amount} MP")
            self.sound_manager.play_combat_sounds("heal")
            self.particle_system.create_heal_effect(self.player.x, self.player.y, mana_amount)
        else:
            self._add_message("No Magic Potion available!")
    
    def _use_strength_potion(self):
        """Use a strength potion"""
        strength_potion = None
        for item in self.player.inventory:
            if item.name == "Strength Potion":
                strength_potion = item
                break
        
        if strength_potion:
            self.player.inventory.remove(strength_potion)
            strength_bonus = 10
            self.player.attack_power += strength_bonus
            self._add_message(f"Used Strength Potion! +{strength_bonus} Attack")
            self.sound_manager.play_combat_sounds("heal")
            self.particle_system.create_heal_effect(self.player.x, self.player.y, strength_bonus)
        else:
            self._add_message("No Strength Potion available!")
    
    def _toggle_quest_log(self):
        """Toggle quest log visibility"""
        self.quest_log_visible = not self.quest_log_visible
        if self.quest_log_visible:
            self._add_message("Quest Log: Press Q to view active quests")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_crafting_menu(self):
        """Toggle crafting menu visibility"""
        self.crafting_menu_visible = not self.crafting_menu_visible
        if self.crafting_menu_visible:
            self._add_message("Crafting: Press C to open crafting menu")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_map(self):
        """Toggle map visibility"""
        self.map_visible = not self.map_visible
        if self.map_visible:
            self._add_message("Map: Press M to view world map")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_settings_menu(self):
        """Toggle settings menu visibility"""
        self.settings_menu_visible = not self.settings_menu_visible
        if self.settings_menu_visible:
            self._add_message("Settings: Press S to open settings")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_save_menu(self):
        """Toggle save menu visibility"""
        self.save_menu_visible = not self.save_menu_visible
        if self.save_menu_visible:
            self._add_message("Save Menu: Press L to save/load games")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_skill_tree(self):
        """Toggle skill tree visibility"""
        self.skill_tree_visible = not self.skill_tree_visible
        if self.skill_tree_visible:
            self._add_message("Skill Tree: Press K to view skills")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_achievements(self):
        """Toggle achievements visibility"""
        self.achievements_visible = not self.achievements_visible
        if self.achievements_visible:
            self._add_message("Achievements: Press A to view achievements")
        self.sound_manager.play_ui_sounds("select")
    
    def _toggle_statistics(self):
        """Toggle statistics visibility"""
        self._add_message("Statistics: Press V to view stats")
        self.sound_manager.play_ui_sounds("select")
        # TODO: Implement statistics menu
    
    def _toggle_trading_menu(self):
        """Toggle trading menu visibility"""
        self.trading_menu_visible = not self.trading_menu_visible
        if self.trading_menu_visible:
            self._add_message("Trading: Press B to open trading menu")
        self.sound_manager.play_ui_sounds("select")
    
    def _handle_quest_log_event(self, event):
        """Handle quest log events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                self.quest_log_visible = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_crafting_menu_event(self, event):
        """Handle crafting menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c or event.key == pygame.K_ESCAPE:
                self.crafting_menu_visible = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_settings_menu_event(self, event):
        """Handle settings menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s or event.key == pygame.K_ESCAPE:
                self.settings_menu_visible = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_map_event(self, event):
        """Handle map events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                self.map_visible = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_save_menu_event(self, event):
        """Handle save menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l or event.key == pygame.K_ESCAPE:
                self.save_menu_visible = False
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
                self.skill_tree_visible = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_achievements_event(self, event):
        """Handle achievements events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_ESCAPE:
                self.achievements_visible = False
                self.sound_manager.play_ui_sounds("select")
                return True
        return False
    
    def _handle_trading_menu_event(self, event):
        """Handle trading menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b or event.key == pygame.K_ESCAPE:
                self.trading_menu_visible = False
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
        if self.weather == "rain":
            # Create rain effect
            for _ in range(50):
                x = random.randint(0, screen.get_width())
                y = random.randint(0, screen.get_height())
                pygame.draw.line(screen, (100, 150, 255), (x, y), (x, y + 10), 1)
        elif self.weather == "storm":
            # Create storm effect (more intense rain)
            for _ in range(100):
                x = random.randint(0, screen.get_width())
                y = random.randint(0, screen.get_height())
                pygame.draw.line(screen, (80, 120, 200), (x, y), (x, y + 15), 2)
        elif self.weather == "fog":
            # Create fog effect
            fog_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            fog_surface.fill((200, 200, 200, 50))
            screen.blit(fog_surface, (0, 0))
    
    def _render_time_display(self, screen):
        """Render time and weather display"""
        font = pygame.font.Font(None, 20)
        
        # Format time
        hours = int(self.time_of_day)
        minutes = int((self.time_of_day - hours) * 60)
        time_text = f"Day {self.day_count} - {hours:02d}:{minutes:02d}"
        
        # Weather text
        weather_text = f"Weather: {self.weather.title()}"
        
        # Render time
        time_surface = font.render(time_text, True, (255, 255, 255))
        screen.blit(time_surface, (screen.get_width() - 200, 10))
        
        # Render weather
        weather_surface = font.render(weather_text, True, (255, 255, 255))
        screen.blit(weather_surface, (screen.get_width() - 200, 35))
    
    def _update_quest_progress(self):
        """Update quest progress based on player actions"""
        # Check for level up
        if self.player.level > getattr(self, '_last_quest_level', 0):
            self.quest_system.on_level_up(self.player.level)
            self._last_quest_level = self.player.level
    
    def _update_weather_and_time(self, dt: float):
        """Update weather and time based on game time"""
        self.weather_timer += dt
        
        if self.weather_timer >= self.weather_duration:
            self.weather_timer = 0
            self.weather = random.choice(["clear", "rain", "storm", "fog"])
            self.weather_duration = random.uniform(300, 600) # 5-10 minutes
            
            if self.weather == "rain":
                self.sound_manager.play_ambient_sounds("rain")
            elif self.weather == "storm":
                self.sound_manager.play_ambient_sounds("storm")
            elif self.weather == "fog":
                self.sound_manager.play_ambient_sounds("fog")
        
        # Update time of day
        self.time_of_day += dt / 60 # 1 second per minute
        if self.time_of_day >= 24:
            self.time_of_day = 0
            self.day_count += 1
            self._add_message(f"New day! Day {self.day_count}")
            self.weather_duration = random.uniform(300, 600) # Reset weather duration for new day
            self.weather = "clear" # Reset weather to clear for new day
            self.sound_manager.play_ambient_sounds("day_start")
        
        # Update lighting based on time
        if 6 <= self.time_of_day < 18: # Day
            self.renderer.set_ambient_light(self.day_light_intensity)
        else: # Night
            self.renderer.set_ambient_light(self.night_light_intensity)
    
    def _update_magic_and_abilities(self, dt: float):
        """Update magic and special abilities cooldowns"""
        # Regenerate mana
        self.player_mana += self.mana_regen_rate * dt
        if self.player_mana > self.player_max_mana:
            self.player_mana = self.player_max_mana
        
        # Update spell cooldowns
        for spell_name in self.spell_cooldowns:
            if self.spell_cooldowns[spell_name] > 0:
                self.spell_cooldowns[spell_name] -= dt
                if self.spell_cooldowns[spell_name] < 0:
                    self.spell_cooldowns[spell_name] = 0
        
        # Update ability cooldowns
        for ability_name, ability_data in self.special_abilities.items():
            if ability_data['cooldown'] > 0:
                ability_data['cooldown'] -= dt
                if ability_data['cooldown'] < 0:
                    ability_data['cooldown'] = 0
    
    def _save_game(self, slot: int):
        """Save game to slot"""
        try:
            game_state = {
                'player': {
                    'x': self.player.x,
                    'y': self.player.y,
                    'health': self.player.health,
                    'max_health': self.player.max_health,
                    'experience': self.player.experience,
                    'level': self.player.level,
                    'attack_power': self.player.attack_power,
                    'defense': self.player.defense,
                    'speed': self.player.speed,
                    'inventory': [item.name for item in self.player.inventory]
                },
                'game_time': self.game_time,
                'score': self.score,
                'stats': self.stats,
                'achievements': self.achievements,
                'player_skills': self.player_skills,
                'time_of_day': self.time_of_day,
                'day_count': self.day_count,
                'weather': self.weather,
                'weather_timer': self.weather_timer,
                'weather_duration': self.weather_duration,
                'player_mana': self.player_mana,
                'player_max_mana': self.player_max_mana,
                'spell_cooldowns': self.spell_cooldowns,
                'special_abilities': self.special_abilities,
                'player_gold': self.player_gold
            }
            
            self.save_system.save_game(slot, game_state)
            self._add_message(f"Game saved to slot {slot}!")
            self.sound_manager.play_ui_sounds("confirm")
        except Exception as e:
            self._add_message(f"Failed to save game: {e}")
    
    def _load_game(self, slot: int):
        """Load game from slot"""
        try:
            if self.save_system.is_slot_empty(slot):
                self._add_message(f"Slot {slot} is empty!")
                return
            
            game_state = self.save_system.load_game(slot)
            
            # Restore player state
            player_data = game_state['player']
            self.player.x = player_data['x']
            self.player.y = player_data['y']
            self.player.health = player_data['health']
            self.player.max_health = player_data['max_health']
            self.player.experience = player_data['experience']
            self.player.level = player_data['level']
            self.player.attack_power = player_data['attack_power']
            self.player.defense = player_data['defense']
            self.player.speed = player_data['speed']
            
            # Restore inventory
            self.player.inventory.clear()
            for item_name in player_data['inventory']:
                # Create item from name (simplified)
                item = ItemFactory.create_item(item_name)
                if item:
                    self.player.inventory.append(item)
            
            # Restore game state
            self.game_time = game_state.get('game_time', 0)
            self.score = game_state.get('score', 0)
            self.stats = game_state.get('stats', self.stats)
            self.achievements = game_state.get('achievements', self.achievements)
            self.player_skills = game_state.get('player_skills', self.player_skills)
            self.time_of_day = game_state.get('time_of_day', 0)
            self.day_count = game_state.get('day_count', 1)
            self.weather = game_state.get('weather', "clear")
            self.weather_timer = game_state.get('weather_timer', 0)
            self.weather_duration = game_state.get('weather_duration', random.uniform(300, 600))
            self.player_mana = game_state.get('player_mana', 100)
            self.player_max_mana = game_state.get('player_max_mana', 100)
            self.spell_cooldowns = game_state.get('spell_cooldowns', self.spell_cooldowns)
            self.special_abilities = game_state.get('special_abilities', self.special_abilities)
            self.player_gold = game_state.get('player_gold', 100)
            
            self._add_message(f"Game loaded from slot {slot}!")
            self.sound_manager.play_ui_sounds("confirm")
        except Exception as e:
            self._add_message(f"Failed to load game: {e}")
    
    def _check_achievements(self):
        """Check and update achievements"""
        # First Blood
        if self.stats['enemies_killed'] >= 1 and not self.achievements['first_blood']['unlocked']:
            self.achievements['first_blood']['unlocked'] = True
            self._add_message("Achievement Unlocked: First Blood!")
            self.sound_manager.play_ui_sounds("level_up")
        
        # Collector
        if self.stats['items_collected'] >= 10 and not self.achievements['collector']['unlocked']:
            self.achievements['collector']['unlocked'] = True
            self._add_message("Achievement Unlocked: Collector!")
            self.sound_manager.play_ui_sounds("level_up")
        
        # Explorer
        if self.stats['areas_explored'] >= 5 and not self.achievements['explorer']['unlocked']:
            self.achievements['explorer']['unlocked'] = True
            self._add_message("Achievement Unlocked: Explorer!")
            self.sound_manager.play_ui_sounds("level_up")
        
        # Craftsman
        if self.stats['items_crafted'] >= 1 and not self.achievements['craftsman']['unlocked']:
            self.achievements['craftsman']['unlocked'] = True
            self._add_message("Achievement Unlocked: Craftsman!")
            self.sound_manager.play_ui_sounds("level_up")
        
        # Survivor
        if self.player.level >= 5 and not self.achievements['survivor']['unlocked']:
            self.achievements['survivor']['unlocked'] = True
            self._add_message("Achievement Unlocked: Survivor!")
            self.sound_manager.play_ui_sounds("level_up")
        
        # Boss Slayer (check if any boss was killed)
        if self.stats['enemies_killed'] >= 10 and not self.achievements['boss_slayer']['unlocked']:
            self.achievements['boss_slayer']['unlocked'] = True
            self._add_message("Achievement Unlocked: Boss Slayer!")
            self.sound_manager.play_ui_sounds("level_up")
    
    def _cast_fireball(self):
        """Cast fireball spell"""
        if self.player_mana >= 20 and self.spell_cooldowns['fireball'] <= 0:
            self.player_mana -= 20
            self.spell_cooldowns['fireball'] = 2.0
            
            # Find nearest enemy
            nearest_enemy = None
            nearest_distance = float('inf')
            
            for enemy in self.enemies:
                if enemy.alive:
                    distance = self.player.distance_to(enemy)
                    if distance < nearest_distance and distance <= 200:
                        nearest_distance = distance
                        nearest_enemy = enemy
            
            if nearest_enemy:
                # Deal magic damage
                damage = 30
                nearest_enemy.take_damage(damage)
                self.stats['damage_dealt'] += damage
                
                # Create fireball effect
                self.particle_system.create_combat_effect(nearest_enemy.x, nearest_enemy.y, "fireball")
                self.sound_manager.play_combat_sounds("attack")
                self._add_message(f"Fireball hit {nearest_enemy.enemy_type} for {damage} damage!")
                
                # Check if enemy died
                if not nearest_enemy.alive:
                    self.stats['enemies_killed'] += 1
                    self.player.gain_experience(25)
                    self._add_message(f"Fireball destroyed {nearest_enemy.enemy_type}!")
            else:
                self._add_message("No enemies in range for fireball!")
        elif self.player_mana < 20:
            self._add_message("Not enough mana for fireball!")
        else:
            self._add_message("Fireball is on cooldown!")
    
    def _cast_ice_bolt(self):
        """Cast ice bolt spell"""
        if self.player_mana >= 15 and self.spell_cooldowns['ice_bolt'] <= 0:
            self.player_mana -= 15
            self.spell_cooldowns['ice_bolt'] = 1.5
            
            # Find nearest enemy
            nearest_enemy = None
            nearest_distance = float('inf')
            
            for enemy in self.enemies:
                if enemy.alive:
                    distance = self.player.distance_to(enemy)
                    if distance < nearest_distance and distance <= 150:
                        nearest_distance = distance
                        nearest_enemy = enemy
            
            if nearest_enemy:
                # Deal magic damage and slow
                damage = 20
                nearest_enemy.take_damage(damage)
                nearest_enemy.speed *= 0.5  # Slow effect
                self.stats['damage_dealt'] += damage
                
                # Create ice effect
                self.particle_system.create_combat_effect(nearest_enemy.x, nearest_enemy.y, "ice")
                self.sound_manager.play_combat_sounds("attack")
                self._add_message(f"Ice bolt hit {nearest_enemy.enemy_type} for {damage} damage!")
            else:
                self._add_message("No enemies in range for ice bolt!")
        elif self.player_mana < 15:
            self._add_message("Not enough mana for ice bolt!")
        else:
            self._add_message("Ice bolt is on cooldown!")
    
    def _cast_lightning(self):
        """Cast lightning spell"""
        if self.player_mana >= 25 and self.spell_cooldowns['lightning'] <= 0:
            self.player_mana -= 25
            self.spell_cooldowns['lightning'] = 3.0
            
            # Deal damage to all enemies in range
            enemies_hit = 0
            total_damage = 0
            
            for enemy in self.enemies:
                if enemy.alive:
                    distance = self.player.distance_to(enemy)
                    if distance <= 120:
                        damage = 25
                        enemy.take_damage(damage)
                        total_damage += damage
                        enemies_hit += 1
                        
                        # Create lightning effect
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
        if self.player_mana >= 30 and self.spell_cooldowns['heal'] <= 0:
            self.player_mana -= 30
            self.spell_cooldowns['heal'] = 5.0
            
            heal_amount = 40
            self.player.heal(heal_amount)
            
            # Create heal effect
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
            dash_distance = 100
            self.player.x += math.cos(self.player.facing_angle) * dash_distance
            self.player.y += math.sin(self.player.facing_angle) * dash_distance
            
            # Create dash effect
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
            original_defense = self.player.defense
            self.player.defense *= 2
            
            # Create shield effect
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
            original_attack = self.player.attack_power
            self.player.attack_power *= 2
            
            # Create rage effect
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
