"""
Advanced rendering system with lighting and visual effects
"""

import pygame
import math
import random
from typing import List, Tuple, Optional, Dict
from game.core.settings import Settings
from game.graphics.sprite_system import SpriteSheet

class Renderer:
    """Advanced rendering system with lighting and effects"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.sprite_sheet = SpriteSheet(settings)
        
        # Lighting system
        self.light_sources: List[Dict] = []
        self.ambient_light = 0.3
        self.light_falloff = 0.1
        
        # Visual effects
        self.screen_shake = 0
        self.fade_alpha = 255
        self.fade_direction = 1  # 1 for fade in, -1 for fade out
        
        # Post-processing effects
        self.bloom_strength = 0.3
        self.contrast = 1.1
        self.saturation = 1.2
        
        # Create light textures
        self._create_light_textures()
    
    def _create_light_textures(self):
        """Create light source textures"""
        # Player light (small, bright)
        self.player_light = pygame.Surface((64, 64), pygame.SRCALPHA)
        for i in range(32):
            alpha = int(255 * (1 - i / 32))
            pygame.draw.circle(self.player_light, (255, 255, 200, alpha), (32, 32), 32 - i)
        
        # Torch light (medium, warm)
        self.torch_light = pygame.Surface((96, 96), pygame.SRCALPHA)
        for i in range(48):
            alpha = int(200 * (1 - i / 48))
            pygame.draw.circle(self.torch_light, (255, 150, 50, alpha), (48, 48), 48 - i)
        
        # Boss light (large, intense)
        self.boss_light = pygame.Surface((128, 128), pygame.SRCALPHA)
        for i in range(64):
            alpha = int(255 * (1 - i / 64))
            pygame.draw.circle(self.boss_light, (255, 100, 100, alpha), (64, 64), 64 - i)
    
    def add_light_source(self, x: float, y: float, light_type: str = "player", intensity: float = 1.0):
        """Add a light source to the scene"""
        self.light_sources.append({
            'x': x,
            'y': y,
            'type': light_type,
            'intensity': intensity,
            'flicker': random.uniform(0.8, 1.2) if light_type == "torch" else 1.0
        })
    
    def clear_lights(self):
        """Clear all light sources"""
        self.light_sources.clear()
    
    def render_world_with_lighting(self, screen: pygame.Surface, world_surface: pygame.Surface, 
                                 camera_offset: Tuple[float, float]):
        """Render the world with dynamic lighting"""
        # Create lighting surface
        light_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        light_surface.fill((0, 0, 0, int(255 * (1 - self.ambient_light))))
        
        # Render light sources
        for light in self.light_sources:
            self._render_light_source(light_surface, light, camera_offset)
        
        # Apply lighting to world
        lit_world = world_surface.copy()
        lit_world.blit(light_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        # Render to screen
        screen.blit(lit_world, (0, 0))
    
    def _render_light_source(self, light_surface: pygame.Surface, light: Dict, 
                           camera_offset: Tuple[float, float]):
        """Render a single light source"""
        screen_x = light['x'] - camera_offset[0]
        screen_y = light['y'] - camera_offset[1]
        
        # Get appropriate light texture
        if light['type'] == "player":
            light_texture = self.player_light
        elif light['type'] == "torch":
            light_texture = self.torch_light
        elif light['type'] == "boss":
            light_texture = self.boss_light
        else:
            light_texture = self.player_light
        
        # Apply flicker effect
        if light['flicker'] != 1.0:
            flickered = light_texture.copy()
            flickered.set_alpha(int(flickered.get_alpha() * light['flicker']))
            light_texture = flickered
        
        # Position light
        light_rect = light_texture.get_rect(center=(screen_x, screen_y))
        light_surface.blit(light_texture, light_rect)
    
    def render_entity_with_effects(self, screen: pygame.Surface, entity_sprite: pygame.Surface,
                                 x: float, y: float, entity_type: str = "player"):
        """Render an entity with visual effects"""
        # Apply screen shake
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        # Add glow effect based on entity type
        if entity_type == "player":
            glow_color = (100, 200, 255, 50)
        elif entity_type == "boss":
            glow_color = (255, 100, 100, 80)
        elif entity_type == "elite":
            glow_color = (255, 215, 0, 60)
        else:
            glow_color = (100, 100, 100, 30)
        
        # Create glow effect
        glow_surface = pygame.Surface(entity_sprite.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, 
                         (entity_sprite.get_width() // 2, entity_sprite.get_height() // 2),
                         entity_sprite.get_width() // 2)
        
        # Render glow
        screen.blit(glow_surface, (x - entity_sprite.get_width() // 2 + shake_x,
                                  y - entity_sprite.get_height() // 2 + shake_y))
        
        # Render entity
        screen.blit(entity_sprite, (x - entity_sprite.get_width() // 2 + shake_x,
                                  y - entity_sprite.get_height() // 2 + shake_y))
    
    def render_particle_effect(self, screen: pygame.Surface, particles: List[Dict]):
        """Render particle effects with advanced visuals"""
        for particle in particles:
            if particle['life'] <= 0:
                continue
            
            # Calculate alpha based on life
            alpha = int(255 * (particle['life'] / particle['max_life']))
            
            # Create particle surface
            particle_surface = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            
            # Particle color based on type
            if particle['type'] == "damage":
                color = (255, 50, 50, alpha)
            elif particle['type'] == "heal":
                color = (50, 255, 50, alpha)
            elif particle['type'] == "level_up":
                color = (255, 255, 50, alpha)
            elif particle['type'] == "combat":
                color = (255, 200, 50, alpha)
            else:
                color = (200, 200, 200, alpha)
            
            # Draw particle
            pygame.draw.circle(particle_surface, color, 
                             (particle['size'] // 2, particle['size'] // 2),
                             particle['size'] // 2)
            
            # Add trail effect
            if particle['type'] in ["combat", "level_up"]:
                trail_length = 8
                for i in range(trail_length):
                    trail_alpha = alpha * (1 - i / trail_length)
                    trail_color = (*color[:3], int(trail_alpha))
                    trail_surface = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surface, trail_color,
                                     (particle['size'] // 2, particle['size'] // 2),
                                     particle['size'] // 2)
                    
                    trail_x = particle['x'] - particle['vx'] * i * 0.1
                    trail_y = particle['y'] - particle['vy'] * i * 0.1
                    screen.blit(trail_surface, (trail_x - particle['size'] // 2,
                                              trail_y - particle['size'] // 2))
            
            # Render particle
            screen.blit(particle_surface, (particle['x'] - particle['size'] // 2,
                                         particle['y'] - particle['size'] // 2))
    
    def render_ui_with_effects(self, screen: pygame.Surface, ui_elements: List[Dict]):
        """Render UI elements with visual effects"""
        for element in ui_elements:
            if element['type'] == "health_bar":
                self._render_health_bar(screen, element)
            elif element['type'] == "exp_bar":
                self._render_exp_bar(screen, element)
            elif element['type'] == "minimap":
                self._render_minimap(screen, element)
            elif element['type'] == "inventory":
                self._render_inventory(screen, element)
    
    def _render_health_bar(self, screen: pygame.Surface, element: Dict):
        """Render health bar with effects"""
        x, y = element['x'], element['y']
        current_health = element['current']
        max_health = element['max']
        
        # Get sprites
        bg_sprite = self.sprite_sheet.get_sprite("health_bg")
        fill_sprite = self.sprite_sheet.get_sprite("health_fill")
        
        if bg_sprite and fill_sprite:
            # Render background
            screen.blit(bg_sprite, (x, y))
            
            # Calculate fill width
            fill_width = int((current_health / max_health) * fill_sprite.get_width())
            if fill_width > 0:
                # Create fill surface
                fill_surface = pygame.Surface((fill_width, fill_sprite.get_height()), pygame.SRCALPHA)
                fill_surface.blit(fill_sprite, (0, 0), (0, 0, fill_width, fill_sprite.get_height()))
                
                # Add pulse effect if health is low
                if current_health / max_health < 0.3:
                    pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 50
                    fill_surface.set_alpha(255 + int(pulse))
                
                screen.blit(fill_surface, (x, y))
    
    def _render_exp_bar(self, screen: pygame.Surface, element: Dict):
        """Render experience bar with effects"""
        x, y = element['x'], element['y']
        current_exp = element['current']
        max_exp = element['max']
        
        # Get sprites
        bg_sprite = self.sprite_sheet.get_sprite("exp_bg")
        fill_sprite = self.sprite_sheet.get_sprite("exp_fill")
        
        if bg_sprite and fill_sprite:
            # Render background
            screen.blit(bg_sprite, (x, y))
            
            # Calculate fill width
            fill_width = int((current_exp / max_exp) * fill_sprite.get_width())
            if fill_width > 0:
                # Create fill surface
                fill_surface = pygame.Surface((fill_width, fill_sprite.get_height()), pygame.SRCALPHA)
                fill_surface.blit(fill_sprite, (0, 0), (0, 0, fill_width, fill_sprite.get_height()))
                
                # Add sparkle effect
                sparkle_alpha = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 100
                fill_surface.set_alpha(255 + int(sparkle_alpha))
                
                screen.blit(fill_surface, (x, y))
    
    def _render_minimap(self, screen: pygame.Surface, element: Dict):
        """Render minimap with effects"""
        x, y = element['x'], element['y']
        size = element.get('size', 150)
        
        # Create minimap surface
        minimap = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw border with glow
        pygame.draw.rect(minimap, (100, 100, 100, 100), (0, 0, size, size))
        pygame.draw.rect(minimap, (200, 200, 200, 150), (0, 0, size, size), 2)
        
        # Add player indicator
        player_x, player_y = element['player_pos']
        pygame.draw.circle(minimap, (100, 200, 255), 
                         (int(player_x * size / element['world_width']),
                          int(player_y * size / element['world_height'])), 3)
        
        # Add pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 50
        minimap.set_alpha(200 + int(pulse))
        
        screen.blit(minimap, (x, y))
    
    def _render_inventory(self, screen: pygame.Surface, element: Dict):
        """Render inventory with effects"""
        if not element.get('visible', False):
            return
        
        x, y = element['x'], element['y']
        width, height = element['width'], element['height']
        
        # Create inventory surface with transparency
        inventory_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw background with gradient
        for i in range(height):
            alpha = 200 - int(i * 0.5)
            pygame.draw.line(inventory_surface, (40, 40, 60, alpha), (0, i), (width, i))
        
        # Draw border with glow
        pygame.draw.rect(inventory_surface, (100, 100, 150, 150), (0, 0, width, height), 3)
        
        screen.blit(inventory_surface, (x, y))
    
    def apply_screen_shake(self, intensity: float):
        """Apply screen shake effect"""
        self.screen_shake = max(0, self.screen_shake - 0.5)
        if intensity > 0:
            self.screen_shake = max(self.screen_shake, intensity)
    
    def apply_fade_effect(self, direction: int, speed: float = 5):
        """Apply fade in/out effect"""
        self.fade_direction = direction
        self.fade_alpha += speed * direction
        self.fade_alpha = max(0, min(255, self.fade_alpha))
    
    def render_fade_overlay(self, screen: pygame.Surface):
        """Render fade overlay"""
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, int(self.fade_alpha)))
            screen.blit(fade_surface, (0, 0))
    
    def apply_post_processing(self, screen: pygame.Surface):
        """Apply post-processing effects"""
        # Simple bloom effect
        if self.bloom_strength > 0:
            bloom_surface = screen.copy()
            bloom_surface.set_alpha(int(255 * self.bloom_strength))
            screen.blit(bloom_surface, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # Apply contrast and saturation (simplified)
        # In a full implementation, this would use pixel manipulation
        pass
