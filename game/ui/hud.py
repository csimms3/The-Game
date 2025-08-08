"""
Heads-Up Display (HUD) system
"""

import pygame
from typing import Tuple, List
from game.core.settings import Settings

class HUD:
    """Heads-Up Display for game information"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # Colors
        self.colors = {
            'health': (255, 50, 50),
            'health_bg': (100, 20, 20),
            'exp': (50, 150, 255),
            'exp_bg': (20, 50, 100),
            'text': (255, 255, 255),
            'text_dim': (200, 200, 200),
            'text_bright': (255, 255, 0),
            'background': (0, 0, 0, 128),
            'border': (100, 100, 100)
        }
        
        # Cached surfaces for performance
        self.cached_surfaces = {}
        self.cache_dirty = True
    
    def render_health_bar(self, screen: pygame.Surface, health: int, max_health: int, 
                         x: int, y: int, width: int = 200, height: int = 20):
        """Render a health bar with smooth animation"""
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, self.colors['health_bg'], bg_rect)
        
        # Health bar
        health_ratio = health / max_health
        health_width = int(width * health_ratio)
        if health_width > 0:
            health_rect = pygame.Rect(x, y, health_width, height)
            pygame.draw.rect(screen, self.colors['health'], health_rect)
        
        # Border
        pygame.draw.rect(screen, self.colors['border'], bg_rect, 2)
        
        # Text
        health_text = f"{health}/{max_health}"
        text_surface = self.font_small.render(health_text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=bg_rect.center)
        screen.blit(text_surface, text_rect)
    
    def render_exp_bar(self, screen: pygame.Surface, exp: int, exp_needed: int,
                      x: int, y: int, width: int = 200, height: int = 15):
        """Render an experience bar"""
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, self.colors['exp_bg'], bg_rect)
        
        # Experience bar
        exp_ratio = exp / exp_needed
        exp_width = int(width * exp_ratio)
        if exp_width > 0:
            exp_rect = pygame.Rect(x, y, exp_width, height)
            pygame.draw.rect(screen, self.colors['exp'], exp_rect)
        
        # Border
        pygame.draw.rect(screen, self.colors['border'], bg_rect, 1)
        
        # Text
        exp_text = f"XP: {exp}/{exp_needed}"
        text_surface = self.font_tiny.render(exp_text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=bg_rect.center)
        screen.blit(text_surface, text_rect)
    
    def render_stats_panel(self, screen: pygame.Surface, player, x: int, y: int):
        """Render player stats in a panel"""
        panel_width = 250
        panel_height = 200
        panel_rect = pygame.Rect(x, y, panel_width, panel_height)
        
        # Semi-transparent background
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(180)
        panel_surface.fill(self.colors['background'])
        screen.blit(panel_surface, (x, y))
        
        # Border
        pygame.draw.rect(screen, self.colors['border'], panel_rect, 2)
        
        # Stats
        stats = [
            f"Level: {player.level}",
            f"Health: {player.health}/{player.max_health}",
            f"Attack: {player.attack_power}",
            f"Defense: {player.defense}",
            f"Speed: {player.speed:.1f}",
            f"Score: {getattr(player, 'score', 0)}"
        ]
        
        for i, stat in enumerate(stats):
            text_surface = self.font_small.render(stat, True, self.colors['text'])
            screen.blit(text_surface, (x + 10, y + 10 + i * 25))
    
    def render_minimap(self, screen: pygame.Surface, world_generator, player, 
                      camera_offset: Tuple[float, float], x: int, y: int, size: int = 150):
        """Render a minimap showing the world and player position"""
        minimap_surface = pygame.Surface((size, size))
        minimap_surface.fill(self.colors['background'])
        
        # Calculate minimap scale
        world_width = world_generator.world_width
        world_height = world_generator.world_height
        scale_x = size / world_width
        scale_y = size / world_height
        
        # Draw terrain (simplified)
        tile_size = world_generator.tile_size
        for tile_y in range(0, world_height // tile_size, 4):  # Sample every 4th tile
            for tile_x in range(0, world_width // tile_size, 4):
                terrain_type = world_generator.terrain_map[tile_y][tile_x]
                color = world_generator.get_terrain_color(terrain_type)
                
                map_x = int(tile_x * tile_size * scale_x)
                map_y = int(tile_y * tile_size * scale_y)
                map_size = max(1, int(tile_size * scale_x))
                
                pygame.draw.rect(minimap_surface, color, 
                               (map_x, map_y, map_size, map_size))
        
        # Draw player position
        player_x = int(player.x * scale_x)
        player_y = int(player.y * scale_y)
        pygame.draw.circle(minimap_surface, (255, 255, 0), (player_x, player_y), 3)
        
        # Draw minimap on screen
        screen.blit(minimap_surface, (x, y))
        pygame.draw.rect(screen, self.colors['border'], (x, y, size, size), 2)
    
    def render_message_log(self, screen: pygame.Surface, messages: List[str], 
                          x: int, y: int, max_messages: int = 5):
        """Render a message log"""
        if not messages:
            return
        
        # Background
        panel_height = max_messages * 25 + 10
        panel_rect = pygame.Rect(x, y, 400, panel_height)
        
        panel_surface = pygame.Surface((400, panel_height))
        panel_surface.set_alpha(180)
        panel_surface.fill(self.colors['background'])
        screen.blit(panel_surface, (x, y))
        
        # Border
        pygame.draw.rect(screen, self.colors['border'], panel_rect, 2)
        
        # Messages
        for i, message in enumerate(messages[-max_messages:]):
            text_surface = self.font_small.render(message, True, self.colors['text'])
            screen.blit(text_surface, (x + 5, y + 5 + i * 25))
    
    def render_controls_help(self, screen: pygame.Surface, x: int, y: int):
        """Render controls help"""
        controls = [
            "WASD: Move",
            "SPACE: Attack",
            "E: Pickup Items",
            "I: Inventory",
            "M: Map",
            "ESC: Pause"
        ]
        
        for i, control in enumerate(controls):
            text_surface = self.font_small.render(control, True, self.colors['text_dim'])
            screen.blit(text_surface, (x, y + i * 20))
    
    def render_item_tooltip(self, screen: pygame.Surface, item, x: int, y: int):
        """Render item tooltip"""
        if not item:
            return
        
        # Get item description
        description = item.get_description()
        lines = description.split('\n')
        
        # Calculate tooltip size
        max_width = 0
        line_surfaces = []
        for line in lines:
            if line.strip():
                surface = self.font_small.render(line, True, self.colors['text'])
                line_surfaces.append(surface)
                max_width = max(max_width, surface.get_width())
        
        tooltip_height = len(line_surfaces) * 20 + 10
        tooltip_width = max_width + 20
        
        # Background
        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height))
        tooltip_surface.set_alpha(230)
        tooltip_surface.fill(self.colors['background'])
        screen.blit(tooltip_surface, (x, y))
        
        # Border
        pygame.draw.rect(screen, self.colors['border'], tooltip_rect, 2)
        
        # Text
        for i, line_surface in enumerate(line_surfaces):
            screen.blit(line_surface, (x + 10, y + 5 + i * 20))
