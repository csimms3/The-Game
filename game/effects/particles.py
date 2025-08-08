"""
Particle system for visual effects
"""

import pygame
import random
import math
from typing import List, Tuple
from game.core.settings import Settings

class Particle:
    """Individual particle"""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: Tuple[int, int, int], lifetime: float, size: int = 2):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = 255
    
    def update(self, dt: float):
        """Update particle physics"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        
        # Fade out
        self.alpha = int((self.lifetime / self.max_lifetime) * 255)
        
        # Gravity effect
        self.vy += 50 * dt  # Gravity
        
        return self.lifetime > 0
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render particle"""
        if self.alpha <= 0:
            return
        
        screen_x = self.x - camera_offset[0]
        screen_y = self.y - camera_offset[1]
        
        # Create surface with alpha
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, self.alpha), 
                         (self.size, self.size), self.size)
        screen.blit(particle_surface, (screen_x - self.size, screen_y - self.size))

class ParticleSystem:
    """Manages particle effects"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.particles: List[Particle] = []
    
    def create_damage_effect(self, x: float, y: float, damage: int):
        """Create damage number effect"""
        # Damage number particles
        for _ in range(5):
            vx = random.uniform(-50, 50)
            vy = random.uniform(-100, -50)
            color = (255, 50, 50)  # Red for damage
            lifetime = random.uniform(1.0, 2.0)
            size = random.randint(2, 4)
            
            particle = Particle(x, y, vx, vy, color, lifetime, size)
            self.particles.append(particle)
    
    def create_heal_effect(self, x: float, y: float, amount: int):
        """Create healing effect"""
        for _ in range(8):
            vx = random.uniform(-30, 30)
            vy = random.uniform(-80, -40)
            color = (50, 255, 50)  # Green for healing
            lifetime = random.uniform(1.5, 2.5)
            size = random.randint(2, 3)
            
            particle = Particle(x, y, vx, vy, color, lifetime, size)
            self.particles.append(particle)
    
    def create_level_up_effect(self, x: float, y: float):
        """Create level up effect"""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = (255, 255, 0)  # Yellow for level up
            lifetime = random.uniform(2.0, 3.0)
            size = random.randint(3, 6)
            
            particle = Particle(x, y, vx, vy, color, lifetime, size)
            self.particles.append(particle)
    
    def create_item_pickup_effect(self, x: float, y: float, item_rarity: str):
        """Create item pickup effect"""
        # Color based on rarity
        colors = {
            'common': (192, 192, 192),
            'uncommon': (0, 255, 0),
            'rare': (0, 100, 255),
            'epic': (150, 0, 255),
            'legendary': (255, 165, 0)
        }
        color = colors.get(item_rarity, colors['common'])
        
        for _ in range(10):
            vx = random.uniform(-40, 40)
            vy = random.uniform(-60, -20)
            lifetime = random.uniform(1.0, 2.0)
            size = random.randint(2, 4)
            
            particle = Particle(x, y, vx, vy, color, lifetime, size)
            self.particles.append(particle)
    
    def create_combat_effect(self, x: float, y: float, effect_type: str = "slash"):
        """Create combat effect"""
        if effect_type == "slash":
            # Slash effect
            for i in range(8):
                angle = (i / 8) * math.pi
                speed = random.uniform(30, 80)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                color = (255, 255, 255)  # White slash
                lifetime = random.uniform(0.5, 1.0)
                size = random.randint(1, 3)
                
                particle = Particle(x, y, vx, vy, color, lifetime, size)
                self.particles.append(particle)
        
        elif effect_type == "impact":
            # Impact effect
            for _ in range(12):
                vx = random.uniform(-100, 100)
                vy = random.uniform(-100, 100)
                color = (255, 200, 100)  # Orange impact
                lifetime = random.uniform(0.3, 0.8)
                size = random.randint(2, 5)
                
                particle = Particle(x, y, vx, vy, color, lifetime, size)
                self.particles.append(particle)
    
    def create_explosion_effect(self, x: float, y: float, intensity: float = 1.0):
        """Create explosion effect"""
        num_particles = int(20 * intensity)
        
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200) * intensity
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Random color for explosion
            colors = [(255, 100, 50), (255, 150, 50), (255, 200, 50)]
            color = random.choice(colors)
            
            lifetime = random.uniform(1.0, 2.5) * intensity
            size = random.randint(3, 8)
            
            particle = Particle(x, y, vx, vy, color, lifetime, size)
            self.particles.append(particle)
    
    def update(self, dt: float):
        """Update all particles"""
        # Update particles and remove dead ones
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render all particles"""
        for particle in self.particles:
            particle.render(screen, camera_offset)
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()
