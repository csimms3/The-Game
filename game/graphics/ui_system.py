"""
Advanced UI system with modern design and animations
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional
from game.core.settings import Settings

class UISystem:
    """Advanced UI system with modern design"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        
        # UI state
        self.active_panels: List[str] = []
        self.animations: Dict[str, Dict] = {}
        self.hover_states: Dict[str, bool] = {}
        
        # Color scheme
        self.colors = {
            'primary': (100, 150, 255),
            'secondary': (80, 120, 200),
            'accent': (255, 200, 100),
            'success': (100, 255, 100),
            'danger': (255, 100, 100),
            'warning': (255, 255, 100),
            'background': (30, 30, 50),
            'surface': (50, 50, 80),
            'text': (255, 255, 255),
            'text_secondary': (200, 200, 200)
        }
        
        # Fonts
        self.fonts = self._create_fonts()
        
        # UI elements cache
        self.ui_cache: Dict[str, pygame.Surface] = {}
        
        self._create_ui_elements()
    
    def _create_fonts(self) -> Dict[str, pygame.font.Font]:
        """Create font hierarchy"""
        # Initialize pygame.font if not already done
        if not pygame.font.get_init():
            pygame.font.init()
        
        return {
            'title': pygame.font.Font(None, 48),
            'heading': pygame.font.Font(None, 32),
            'subheading': pygame.font.Font(None, 24),
            'body': pygame.font.Font(None, 18),
            'small': pygame.font.Font(None, 14),
            'tiny': pygame.font.Font(None, 12)
        }
    
    def _create_ui_elements(self):
        """Create reusable UI elements"""
        # Button templates
        self._create_button_templates()
        
        # Panel templates
        self._create_panel_templates()
        
        # Icon templates
        self._create_icon_templates()
    
    def _create_button_templates(self):
        """Create button templates with different styles"""
        # Primary button
        primary_btn = pygame.Surface((120, 40), pygame.SRCALPHA)
        self._draw_rounded_rect(primary_btn, (0, 0, 120, 40), self.colors['primary'], 8)
        self._draw_rounded_rect(primary_btn, (2, 2, 116, 36), self.colors['secondary'], 6)
        self.ui_cache['button_primary'] = primary_btn
        
        # Secondary button
        secondary_btn = pygame.Surface((120, 40), pygame.SRCALPHA)
        self._draw_rounded_rect(secondary_btn, (0, 0, 120, 40), self.colors['surface'], 8)
        self._draw_rounded_rect(secondary_btn, (2, 2, 116, 36), self.colors['background'], 6)
        self.ui_cache['button_secondary'] = secondary_btn
        
        # Danger button
        danger_btn = pygame.Surface((120, 40), pygame.SRCALPHA)
        self._draw_rounded_rect(danger_btn, (0, 0, 120, 40), self.colors['danger'], 8)
        self._draw_rounded_rect(danger_btn, (2, 2, 116, 36), (200, 80, 80), 6)
        self.ui_cache['button_danger'] = danger_btn
    
    def _create_panel_templates(self):
        """Create panel templates"""
        # Main panel
        main_panel = pygame.Surface((300, 200), pygame.SRCALPHA)
        self._draw_rounded_rect(main_panel, (0, 0, 300, 200), self.colors['surface'], 12)
        self._draw_rounded_rect(main_panel, (2, 2, 296, 196), self.colors['background'], 10)
        self.ui_cache['panel_main'] = main_panel
        
        # Small panel
        small_panel = pygame.Surface((200, 150), pygame.SRCALPHA)
        self._draw_rounded_rect(small_panel, (0, 0, 200, 150), self.colors['surface'], 8)
        self._draw_rounded_rect(small_panel, (2, 2, 196, 146), self.colors['background'], 6)
        self.ui_cache['panel_small'] = small_panel
    
    def _create_icon_templates(self):
        """Create icon templates"""
        # Health icon
        health_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(health_icon, self.colors['danger'], (8, 8), 6)
        pygame.draw.circle(health_icon, (255, 100, 100), (8, 8), 4)
        self.ui_cache['icon_health'] = health_icon
        
        # Experience icon
        exp_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(exp_icon, self.colors['primary'], (8, 8), 6)
        pygame.draw.circle(exp_icon, (150, 200, 255), (8, 8), 4)
        self.ui_cache['icon_exp'] = exp_icon
        
        # Inventory icon
        inv_icon = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(inv_icon, self.colors['accent'], (2, 2, 12, 12))
        pygame.draw.rect(inv_icon, (255, 220, 120), (4, 4, 8, 8))
        self.ui_cache['icon_inventory'] = inv_icon
    
    def _draw_rounded_rect(self, surface: pygame.Surface, rect: Tuple[int, int, int, int], 
                          color: Tuple[int, int, int], radius: int):
        """Draw a rounded rectangle"""
        x, y, width, height = rect
        
        # Draw main rectangle
        pygame.draw.rect(surface, color, (x + radius, y, width - 2 * radius, height))
        pygame.draw.rect(surface, color, (x, y + radius, width, height - 2 * radius))
        
        # Draw corner circles
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)
    
    def render_main_menu(self, screen: pygame.Surface, selected_option: int):
        """Render the main menu with modern design"""
        # Background gradient
        self._draw_gradient_background(screen, self.colors['background'], self.colors['surface'])
        
        # Title with glow effect
        title_text = self.fonts['title'].render("THE GAME", True, self.colors['text'])
        title_glow = self.fonts['title'].render("THE GAME", True, self.colors['primary'])
        
        # Apply glow effect
        for i in range(3):
            glow_alpha = 100 - i * 30
            glow_surface = title_glow.copy()
            glow_surface.set_alpha(glow_alpha)
            screen.blit(glow_surface, (screen.get_width() // 2 - title_text.get_width() // 2 + i,
                                      screen.get_height() // 4 + i))
        
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2,
                                screen.get_height() // 4))
        
        # Menu options
        options = ["Campaign", "Open World", "Settings", "Quit"]
        option_y = screen.get_height() // 2
        
        for i, option in enumerate(options):
            is_selected = i == selected_option
            color = self.colors['accent'] if is_selected else self.colors['text']
            
            # Create option background
            option_surface = pygame.Surface((200, 50), pygame.SRCALPHA)
            if is_selected:
                self._draw_rounded_rect(option_surface, (0, 0, 200, 50), self.colors['primary'], 8)
                self._draw_rounded_rect(option_surface, (2, 2, 196, 46), self.colors['secondary'], 6)
            
            # Render text
            text = self.fonts['subheading'].render(option, True, color)
            text_rect = text.get_rect(center=(100, 25))
            option_surface.blit(text, text_rect)
            
            # Add hover effect
            if is_selected:
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 30
                option_surface.set_alpha(255 + int(pulse))
            
            screen.blit(option_surface, (screen.get_width() // 2 - 100, option_y + i * 60))
    
    def render_game_hud(self, screen: pygame.Surface, player_data: Dict, game_data: Dict):
        """Render the game HUD with modern design"""
        # Health bar
        self._render_health_bar(screen, player_data)
        
        # Experience bar
        self._render_experience_bar(screen, player_data)
        
        # Stats panel
        self._render_stats_panel(screen, player_data)
        
        # Minimap
        self._render_minimap(screen, game_data)
        
        # Quick actions
        self._render_quick_actions(screen)
    
    def _render_health_bar(self, screen: pygame.Surface, player_data: Dict):
        """Render health bar with modern design"""
        x, y = 20, 20
        width, height = 200, 20
        
        # Background
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self._draw_rounded_rect(bg_surface, (0, 0, width, height), self.colors['surface'], 10)
        screen.blit(bg_surface, (x, y))
        
        # Health fill
        health_ratio = player_data['health'] / player_data['max_health']
        fill_width = int(width * health_ratio)
        
        if fill_width > 0:
            fill_surface = pygame.Surface((fill_width, height), pygame.SRCALPHA)
            
            # Gradient fill
            for i in range(fill_width):
                if health_ratio > 0.5:
                    color = (100, 255, 100)
                elif health_ratio > 0.25:
                    color = (255, 255, 100)
                else:
                    color = (255, 100, 100)
                
                pygame.draw.line(fill_surface, color, (i, 0), (i, height))
            
            self._draw_rounded_rect(fill_surface, (0, 0, fill_width, height), color, 10)
            screen.blit(fill_surface, (x, y))
        
        # Health icon
        icon = self.ui_cache.get('icon_health')
        if icon:
            screen.blit(icon, (x - 20, y + 2))
        
        # Health text
        health_text = f"{player_data['health']}/{player_data['max_health']}"
        text_surface = self.fonts['small'].render(health_text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(text_surface, text_rect)
    
    def _render_experience_bar(self, screen: pygame.Surface, player_data: Dict):
        """Render experience bar with modern design"""
        x, y = 20, 50
        width, height = 200, 12
        
        # Background
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self._draw_rounded_rect(bg_surface, (0, 0, width, height), self.colors['surface'], 6)
        screen.blit(bg_surface, (x, y))
        
        # Experience fill
        exp_ratio = player_data['experience'] / player_data['experience_to_next']
        fill_width = int(width * exp_ratio)
        
        if fill_width > 0:
            fill_surface = pygame.Surface((fill_width, height), pygame.SRCALPHA)
            
            # Animated gradient
            time_offset = pygame.time.get_ticks() * 0.001
            for i in range(fill_width):
                color_intensity = int(100 + 50 * math.sin(time_offset + i * 0.1))
                color = (100, color_intensity, 255)
                pygame.draw.line(fill_surface, color, (i, 0), (i, height))
            
            self._draw_rounded_rect(fill_surface, (0, 0, fill_width, height), self.colors['primary'], 6)
            screen.blit(fill_surface, (x, y))
        
        # Experience icon
        icon = self.ui_cache.get('icon_exp')
        if icon:
            screen.blit(icon, (x - 20, y))
    
    def _render_stats_panel(self, screen: pygame.Surface, player_data: Dict):
        """Render stats panel with modern design"""
        x, y = 20, 80
        width, height = 150, 100
        
        # Panel background
        panel = self.ui_cache.get('panel_small')
        if panel:
            screen.blit(panel, (x, y))
        
        # Stats text
        stats = [
            f"Level: {player_data['level']}",
            f"Attack: {player_data['attack']}",
            f"Defense: {player_data['defense']}",
            f"Speed: {player_data['speed']}"
        ]
        
        for i, stat in enumerate(stats):
            text_surface = self.fonts['small'].render(stat, True, self.colors['text'])
            screen.blit(text_surface, (x + 10, y + 10 + i * 20))
    
    def _render_minimap(self, screen: pygame.Surface, game_data: Dict):
        """Render minimap with modern design"""
        x, y = screen.get_width() - 170, 20
        size = 150
        
        # Minimap background
        minimap_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        self._draw_rounded_rect(minimap_surface, (0, 0, size, size), self.colors['surface'], 8)
        self._draw_rounded_rect(minimap_surface, (2, 2, size - 4, size - 4), self.colors['background'], 6)
        
        # Add player position
        player_x, player_y = game_data.get('player_pos', (0, 0))
        map_x = int(player_x * size / game_data.get('world_width', 1000))
        map_y = int(player_y * size / game_data.get('world_height', 1000))
        
        pygame.draw.circle(minimap_surface, self.colors['primary'], (map_x, map_y), 3)
        
        # Add pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 50
        minimap_surface.set_alpha(200 + int(pulse))
        
        screen.blit(minimap_surface, (x, y))
    
    def _render_quick_actions(self, screen: pygame.Surface):
        """Render quick action buttons"""
        actions = [
            ("I", "Inventory"),
            ("F", "Heal"),
            ("Q", "Quests"),
            ("C", "Craft")
        ]
        
        x, y = screen.get_width() - 120, screen.get_height() - 120
        
        for i, (key, label) in enumerate(actions):
            # Button background
            btn_surface = pygame.Surface((100, 30), pygame.SRCALPHA)
            self._draw_rounded_rect(btn_surface, (0, 0, 100, 30), self.colors['surface'], 6)
            
            # Key text
            key_text = self.fonts['body'].render(key, True, self.colors['accent'])
            key_rect = key_text.get_rect(center=(50, 10))
            btn_surface.blit(key_text, key_rect)
            
            # Label text
            label_text = self.fonts['small'].render(label, True, self.colors['text'])
            label_rect = label_text.get_rect(center=(50, 20))
            btn_surface.blit(label_text, label_rect)
            
            screen.blit(btn_surface, (x, y + i * 35))
    
    def _draw_gradient_background(self, screen: pygame.Surface, color1: Tuple[int, int, int], 
                                color2: Tuple[int, int, int]):
        """Draw a gradient background"""
        for y in range(screen.get_height()):
            ratio = y / screen.get_height()
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (screen.get_width(), y))
    
    def render_inventory(self, screen: pygame.Surface, inventory_data: Dict):
        """Render inventory with modern design"""
        if not inventory_data.get('visible', False):
            return
        
        # Inventory panel
        panel_width, panel_height = 400, 300
        x = (screen.get_width() - panel_width) // 2
        y = (screen.get_height() - panel_height) // 2
        
        # Background with blur effect
        bg_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        self._draw_rounded_rect(bg_surface, (0, 0, panel_width, panel_height), 
                               (20, 20, 40, 200), 15)
        screen.blit(bg_surface, (x, y))
        
        # Title
        title_text = self.fonts['heading'].render("Inventory", True, self.colors['text'])
        title_rect = title_text.get_rect(center=(x + panel_width // 2, y + 20))
        screen.blit(title_text, title_rect)
        
        # Items grid
        items = inventory_data.get('items', [])
        grid_x, grid_y = x + 20, y + 60
        items_per_row = 8
        
        for i, item in enumerate(items):
            item_x = grid_x + (i % items_per_row) * 45
            item_y = grid_y + (i // items_per_row) * 45
            
            # Item slot
            slot_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
            self._draw_rounded_rect(slot_surface, (0, 0, 40, 40), self.colors['surface'], 6)
            screen.blit(slot_surface, (item_x, item_y))
            
            # Item icon (placeholder)
            icon_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(icon_surface, self.colors['primary'], (15, 15), 12)
            screen.blit(icon_surface, (item_x + 5, item_y + 5))
    
    def render_pause_menu(self, screen: pygame.Surface, selected_option: int):
        """Render pause menu with modern design"""
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Menu panel
        panel_width, panel_height = 300, 250
        x = (screen.get_width() - panel_width) // 2
        y = (screen.get_height() - panel_height) // 2
        
        panel = self.ui_cache.get('panel_main')
        if panel:
            screen.blit(panel, (x, y))
        
        # Title
        title_text = self.fonts['heading'].render("PAUSED", True, self.colors['text'])
        title_rect = title_text.get_rect(center=(x + panel_width // 2, y + 30))
        screen.blit(title_text, title_rect)
        
        # Options
        options = ["Resume", "Settings", "Main Menu", "Quit"]
        option_y = y + 80
        
        for i, option in enumerate(options):
            is_selected = i == selected_option
            color = self.colors['accent'] if is_selected else self.colors['text']
            
            # Option background
            option_surface = pygame.Surface((250, 40), pygame.SRCALPHA)
            if is_selected:
                self._draw_rounded_rect(option_surface, (0, 0, 250, 40), self.colors['primary'], 8)
            
            # Option text
            text = self.fonts['subheading'].render(option, True, color)
            text_rect = text.get_rect(center=(125, 20))
            option_surface.blit(text, text_rect)
            
            screen.blit(option_surface, (x + 25, option_y + i * 50))
