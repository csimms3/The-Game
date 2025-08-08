"""
Enemy entities
"""

import pygame
import math
import random
from typing import List, Tuple, Optional
from game.entities.entity import Entity
from game.core.settings import Settings

class Enemy(Entity):
    """Base enemy class"""
    
    def __init__(self, x: float, y: float, settings: Settings, enemy_type: str = "basic"):
        super().__init__(x, y, settings)
        
        # Make enemies larger
        self.width = 48  # Increased from 32
        self.height = 48  # Increased from 32
        
        self.enemy_type = enemy_type
        self.speed = settings.ENEMY_SPEED
        
        # Combat stats
        self.attack_power = settings.ENEMY_ATTACK_POWER
        self.attack_damage = 10
        
        # AI behavior
        self.detection_range = 150
        self.attack_range = 40
        self.attack_cooldown = 0
        self.last_attack_time = 0
        
        # Movement
        self.target = None
        self.patrol_points = []
        self.current_patrol_index = 0
        self.patrol_timer = 0
        self.patrol_delay = 2.0
        
        # Animation
        self.animation_frames = 4
        self.animation_speed = 0.2
        
        # Create enemy sprite based on type
        self._create_sprite()
    
    def _create_sprite(self):
        """Create enemy sprite based on type"""
        self.sprite = pygame.Surface((self.width, self.height))
        
        if self.enemy_type == "goblin":
            self.sprite.fill(self.settings.GREEN)
            self.attack_damage = 8
            self.speed = self.settings.ENEMY_SPEED * 0.8
        elif self.enemy_type == "orc":
            self.sprite.fill(self.settings.RED)
            self.attack_damage = 15
            self.speed = self.settings.ENEMY_SPEED * 0.6
            self.max_health = 150
            self.health = self.max_health
        elif self.enemy_type == "skeleton":
            self.sprite.fill(self.settings.GRAY)
            self.attack_damage = 12
            self.speed = self.settings.ENEMY_SPEED * 1.2
        else:  # basic
            self.sprite.fill(self.settings.RED)
        
        # Add border and details
        pygame.draw.rect(self.sprite, self.settings.WHITE, 
                        (2, 2, self.width - 4, self.height - 4))
        
        # Add eyes
        eye_size = 4
        pygame.draw.circle(self.sprite, self.settings.BLACK, 
                         (self.width // 3, self.height // 3), eye_size)
        pygame.draw.circle(self.sprite, self.settings.BLACK, 
                         (2 * self.width // 3, self.height // 3), eye_size)
    
    def update(self, dt: float):
        """Update enemy AI and behavior"""
        if not self.alive:
            return
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % self.animation_frames
        
        # AI behavior
        if self.target and self.target.alive:
            self._chase_target(dt)
        else:
            self._patrol(dt)
    
    def _chase_target(self, dt: float):
        """Chase the target player"""
        if not self.target:
            return
        
        # Calculate direction to target
        target_center = self.target.get_center()
        my_center = self.get_center()
        
        dx = target_center[0] - my_center[0]
        dy = target_center[1] - my_center[1]
        
        # Normalize direction
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Move towards target
        move_x = dx * self.speed * dt
        move_y = dy * self.speed * dt
        
        self.move(move_x, move_y)
        
        # Attack if in range
        if distance <= self.attack_range and self.attack_cooldown <= 0:
            self._attack_target()
    
    def _patrol(self, dt: float):
        """Patrol behavior when no target"""
        if not self.patrol_points:
            return
        
        self.patrol_timer += dt
        
        if self.patrol_timer >= self.patrol_delay:
            self.patrol_timer = 0
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        
        # Move towards current patrol point
        target_point = self.patrol_points[self.current_patrol_index]
        dx = target_point[0] - self.x
        dy = target_point[1] - self.y
        
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 10:  # If not close enough to patrol point
            if distance > 0:
                dx /= distance
                dy /= distance
            
            move_x = dx * self.speed * 0.5 * dt
            move_y = dy * self.speed * 0.5 * dt
            self.move(move_x, move_y)
    
    def _attack_target(self):
        """Attack the target"""
        if not self.target or self.attack_cooldown > 0:
            return
        
        # Apply damage to target
        self.target.take_damage(self.attack_damage)
        
        # Set cooldown
        self.attack_cooldown = 1.0
    
    def set_target(self, target: Entity):
        """Set the target to chase"""
        self.target = target
    
    def set_patrol_points(self, points: List[Tuple[float, float]]):
        """Set patrol points for the enemy"""
        self.patrol_points = points
    
    def can_detect_target(self, target: Entity) -> bool:
        """Check if enemy can detect target"""
        if not target.alive:
            return False
        
        distance = self.distance_to(target)
        return distance <= self.detection_range
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render the enemy"""
        if not self.visible or not self.alive:
            return
        
        # Calculate screen position
        screen_x = self.x - camera_offset[0]
        screen_y = self.y - camera_offset[1]
        
        # Draw enemy sprite
        screen.blit(self.sprite, (screen_x, screen_y))
        
        # Draw health bar
        self._draw_health_bar(screen, screen_x, screen_y)
    
    def _draw_health_bar(self, screen: pygame.Surface, x: float, y: float):
        """Draw enemy health bar"""
        bar_width = self.width
        bar_height = 4
        bar_y = y - 8
        
        # Background
        pygame.draw.rect(screen, self.settings.RED, 
                        (x, bar_y, bar_width, bar_height))
        
        # Health
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, self.settings.GREEN, 
                        (x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, self.settings.WHITE, 
                        (x, bar_y, bar_width, bar_height), 1)

class EnemySpawner:
    """Manages enemy spawning"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enemy_types = ["basic", "goblin", "orc", "skeleton"]
        self.spawn_timer = 0
        self.spawn_delay = 5.0  # Spawn every 5 seconds
        self.max_enemies = 10
    
    def update(self, dt: float, enemies: List[Enemy], player_pos: Tuple[float, float]):
        """Update spawner logic"""
        self.spawn_timer += dt
        
        if self.spawn_timer >= self.spawn_delay and len(enemies) < self.max_enemies:
            self._spawn_enemy(enemies, player_pos)
            self.spawn_timer = 0
    
    def _spawn_enemy(self, enemies: List[Enemy], player_pos: Tuple[float, float]):
        """Spawn a new enemy"""
        # Spawn enemy away from player
        spawn_distance = 300
        angle = random.uniform(0, 2 * math.pi)
        
        spawn_x = player_pos[0] + math.cos(angle) * spawn_distance
        spawn_y = player_pos[1] + math.sin(angle) * spawn_distance
        
        # Choose random enemy type
        enemy_type = random.choice(self.enemy_types)
        
        # Create enemy
        enemy = Enemy(spawn_x, spawn_y, self.settings, enemy_type)
        
        # Set patrol points
        patrol_points = []
        for _ in range(3):
            patrol_x = spawn_x + random.uniform(-100, 100)
            patrol_y = spawn_y + random.uniform(-100, 100)
            patrol_points.append((patrol_x, patrol_y))
        
        enemy.set_patrol_points(patrol_points)
        enemies.append(enemy)
