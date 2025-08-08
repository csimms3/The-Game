"""
Main menu state
"""

import pygame
from game.states.base_state import BaseState

class MenuState(BaseState):
    """Main menu state"""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.selected_option = 0
        self.options = [
            "Campaign Mode",
            "Open World Mode",
            "Settings",
            "Quit"
        ]
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Animation variables
        self.title_y = -100
        self.title_target_y = 100
        self.animation_speed = 5
        
    def enter(self):
        """Called when entering menu state"""
        self.logger.info("Entering menu state")
        self.selected_option = 0
        self.title_y = -100
    
    def exit(self):
        """Called when exiting menu state"""
        self.logger.info("Exiting menu state")
    
    def handle_event(self, event):
        """Handle menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._select_option()
            elif event.key == pygame.K_ESCAPE:
                self.game_engine.quit()
    
    def _select_option(self):
        """Handle option selection"""
        if self.selected_option == 0:  # Campaign Mode
            self.game_engine.game_mode = self.settings.MODE_CAMPAIGN
            self.game_engine.change_state('game')
        elif self.selected_option == 1:  # Open World Mode
            self.game_engine.game_mode = self.settings.MODE_OPEN_WORLD
            self.game_engine.change_state('game')
        elif self.selected_option == 2:  # Settings
            # TODO: Implement settings menu
            pass
        elif self.selected_option == 3:  # Quit
            self.game_engine.quit()
    
    def update(self, dt: float):
        """Update menu animations"""
        # Animate title
        if self.title_y < self.title_target_y:
            self.title_y += self.animation_speed * dt * 60  # Scale by dt and FPS
    
    def render(self, screen):
        """Render the menu"""
        # Draw background gradient
        for y in range(self.settings.SCREEN_HEIGHT):
            color_ratio = y / self.settings.SCREEN_HEIGHT
            r = int(20 + color_ratio * 30)
            g = int(30 + color_ratio * 40)
            b = int(50 + color_ratio * 60)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.settings.SCREEN_WIDTH, y))
        
        # Draw title
        title_text = self.font_large.render("THE GAME", True, self.settings.WHITE)
        title_rect = title_text.get_rect(center=(self.settings.SCREEN_WIDTH // 2, self.title_y))
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.font_small.render("Roguelike Adventure", True, self.settings.WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(self.settings.SCREEN_WIDTH // 2, self.title_y + 80))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw menu options
        menu_y = 300
        for i, option in enumerate(self.options):
            # Use bright colors for better readability
            if i == self.selected_option:
                color = (255, 255, 0)  # Bright yellow for selected
                bg_color = (100, 100, 100)  # Dark gray background
            else:
                color = (200, 200, 200)  # Light gray for unselected
                bg_color = None
            
            text = self.font_medium.render(option, True, color)
            rect = text.get_rect(center=(self.settings.SCREEN_WIDTH // 2, menu_y + i * 60))
            
            # Draw background for selected option
            if bg_color:
                bg_rect = pygame.Rect(rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10)
                pygame.draw.rect(screen, bg_color, bg_rect)
                pygame.draw.rect(screen, self.settings.WHITE, bg_rect, 2)
            
            # Draw selection indicator
            if i == self.selected_option:
                indicator_rect = pygame.Rect(rect.left - 30, rect.centery - 3, 15, 6)
                pygame.draw.rect(screen, (255, 255, 0), indicator_rect)
            
            screen.blit(text, rect)
        
        # Draw instructions with better colors
        instructions = [
            "Use ↑↓ to navigate",
            "Press ENTER to select",
            "Press ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, (255, 255, 255))
            rect = text.get_rect(center=(self.settings.SCREEN_WIDTH // 2, 
                                       self.settings.SCREEN_HEIGHT - 100 + i * 30))
            screen.blit(text, rect)
