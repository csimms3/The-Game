"""
Player entity
"""

import pygame
import math
from typing import List, Tuple, Optional
from game.entities.entity import Entity
from game.core.settings import Settings
from game.items.item import Item

class Player(Entity):
    """Player character entity"""
    
    def __init__(self, x: float, y: float, settings: Settings):
        super().__init__(x, y, settings)
        
        # Player specific stats
        self.max_health = 150
        self.health = self.max_health
        self.attack_power = 15
        self.defense = 8
        self.speed = settings.PLAYER_SPEED
        
        # Experience and leveling
        self.experience = 0
        self.level = 1
        self.experience_to_next_level = 100
        
        # Inventory
        self.inventory: List[Item] = []
        self.max_inventory_size = 20
        self.equipped_weapon: Optional[Item] = None
        self.equipped_armor: Optional[Item] = None
        
        # Combat
        self.attack_cooldown = 0
        self.attack_range = 50
        self.last_attack_time = 0
        
        # Movement
        self.facing_direction = 0  # 0: right, 1: down, 2: left, 3: up
        self.is_moving = False
        
        # Animation
        self.animation_frames = 4
        self.animation_speed = 0.15
        
        # Create player sprite (simple colored rectangle for now)
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(settings.BLUE)
        pygame.draw.rect(self.sprite, settings.WHITE, (2, 2, self.width - 4, self.height - 4))
    
    def update(self, dt: float):
        """Update player logic"""
        # Handle movement
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed * dt
            self.facing_direction = 3
            self.is_moving = True
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed * dt
            self.facing_direction = 1
            self.is_moving = True
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed * dt
            self.facing_direction = 2
            self.is_moving = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed * dt
            self.facing_direction = 0
            self.is_moving = True
        else:
            self.is_moving = False
        
        # Update position
        if dx != 0 or dy != 0:
            self.move(dx, dy)
        
        # Update animation
        if self.is_moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % self.animation_frames
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render the player"""
        if not self.visible:
            return
        
        # Calculate screen position
        screen_x = self.x - camera_offset[0]
        screen_y = self.y - camera_offset[1]
        
        # Draw player sprite
        screen.blit(self.sprite, (screen_x, screen_y))
        
        # Draw health bar
        self._draw_health_bar(screen, screen_x, screen_y)
        
        # Draw level indicator
        self._draw_level_indicator(screen, screen_x, screen_y)
    
    def _draw_health_bar(self, screen: pygame.Surface, x: float, y: float):
        """Draw player health bar"""
        bar_width = self.width
        bar_height = 6
        bar_y = y - 10
        
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
    
    def _draw_level_indicator(self, screen: pygame.Surface, x: float, y: float):
        """Draw player level indicator"""
        font = pygame.font.Font(None, 24)
        level_text = font.render(f"Lv.{self.level}", True, self.settings.WHITE)
        text_rect = level_text.get_rect(center=(x + self.width // 2, y - 25))
        screen.blit(level_text, text_rect)
    
    def attack(self, target: Entity) -> bool:
        """Attack a target entity"""
        if self.attack_cooldown > 0:
            return False
        
        distance = self.distance_to(target)
        if distance > self.attack_range:
            return False
        
        # Calculate damage
        damage = self.attack_power
        if self.equipped_weapon:
            damage += self.equipped_weapon.attack_bonus
        
        # Apply damage
        target.take_damage(damage)
        
        # Set cooldown
        self.attack_cooldown = 0.5
        
        return True
    
    def gain_experience(self, amount: int):
        """Gain experience and level up if needed"""
        self.experience += amount
        
        while self.experience >= self.experience_to_next_level:
            self.level_up()
    
    def level_up(self):
        """Level up the player"""
        self.experience -= self.experience_to_next_level
        self.level += 1
        
        # Increase stats
        self.max_health += 10
        self.health = self.max_health
        self.attack_power += 2
        self.defense += 1
        
        # Increase experience requirement
        self.experience_to_next_level = int(self.experience_to_next_level * 1.2)
    
    def add_item_to_inventory(self, item: Item) -> bool:
        """Add item to inventory"""
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return True
        return False
    
    def remove_item_from_inventory(self, item: Item) -> bool:
        """Remove item from inventory"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def equip_item(self, item: Item) -> bool:
        """Equip an item"""
        if item not in self.inventory:
            return False
        
        if item.item_type == "weapon":
            if self.equipped_weapon:
                self.inventory.append(self.equipped_weapon)
            self.equipped_weapon = item
            self.inventory.remove(item)
            return True
        elif item.item_type == "armor":
            if self.equipped_armor:
                self.inventory.append(self.equipped_armor)
            self.equipped_armor = item
            self.inventory.remove(item)
            return True
        
        return False
