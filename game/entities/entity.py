"""
Base entity class
"""

import pygame
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from game.core.settings import Settings

class Entity(ABC):
    """Base class for all game entities"""
    
    def __init__(self, x: float, y: float, settings: Settings):
        self.x = x
        self.y = y
        self.settings = settings
        self.width = settings.TILE_SIZE
        self.height = settings.TILE_SIZE
        
        # Movement
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.speed = 0.0
        
        # Health and combat
        self.max_health = 100
        self.health = self.max_health
        self.attack_power = 10
        self.defense = 5
        
        # State
        self.alive = True
        self.visible = True
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1
        
        # Collision
        self.collision_rect = pygame.Rect(x, y, self.width, self.height)
    
    @abstractmethod
    def update(self, dt: float):
        """Update entity logic"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render the entity"""
        pass
    
    def move(self, dx: float, dy: float):
        """Move entity by delta"""
        self.x += dx
        self.y += dy
        self.collision_rect.x = self.x
        self.collision_rect.y = self.y
    
    def take_damage(self, damage: int) -> bool:
        """Take damage and return True if entity dies"""
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        return False
    
    def heal(self, amount: int):
        """Heal the entity"""
        self.health = min(self.max_health, self.health + amount)
    
    def is_colliding_with(self, other: 'Entity') -> bool:
        """Check collision with another entity"""
        return self.collision_rect.colliderect(other.collision_rect)
    
    def get_center(self) -> Tuple[float, float]:
        """Get entity center position"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def distance_to(self, other: 'Entity') -> float:
        """Calculate distance to another entity"""
        center1 = self.get_center()
        center2 = other.get_center()
        return ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
