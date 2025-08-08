"""
Pause state
"""

import pygame
from game.states.base_state import BaseState

class PauseState(BaseState):
    """Pause menu state"""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.selected_option = 0
        self.options = [
            "Resume",
            "Settings",
            "Main Menu",
            "Quit"
        ]
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Semi-transparent overlay
        self.overlay = pygame.Surface((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
        self.overlay.set_alpha(128)
        self.overlay.fill(self.settings.BLACK)
    
    def enter(self):
        """Called when entering pause state"""
        self.logger.info("Entering pause state")
        self.selected_option = 0
    
    def exit(self):
        """Called when exiting pause state"""
        self.logger.info("Exiting pause state")
    
    def handle_event(self, event):
        """Handle pause events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._select_option()
            elif event.key == pygame.K_ESCAPE:
                self.game_engine.change_state('game')
    
    def _select_option(self):
        """Handle option selection"""
        if self.selected_option == 0:  # Resume
            self.game_engine.change_state('game')
        elif self.selected_option == 1:  # Settings
            # TODO: Implement settings menu
            pass
        elif self.selected_option == 2:  # Main Menu
            self.game_engine.change_state('menu')
        elif self.selected_option == 3:  # Quit
            self.game_engine.quit()
    
    def update(self):
        """Update pause state"""
        pass
    
    def render(self, screen):
        """Render the pause menu"""
        # Draw semi-transparent overlay
        screen.blit(self.overlay, (0, 0))
        
        # Draw pause title
        title_text = self.font_large.render("PAUSED", True, self.settings.WHITE)
        title_rect = title_text.get_rect(center=(self.settings.SCREEN_WIDTH // 2, 200))
        screen.blit(title_text, title_rect)
        
        # Draw menu options
        menu_y = 350
        for i, option in enumerate(self.options):
            color = self.settings.WHITE if i == self.selected_option else self.settings.GRAY
            text = self.font_medium.render(option, True, color)
            rect = text.get_rect(center=(self.settings.SCREEN_WIDTH // 2, menu_y + i * 60))
            
            # Draw selection indicator
            if i == self.selected_option:
                indicator_rect = pygame.Rect(rect.left - 20, rect.centery - 2, 10, 4)
                pygame.draw.rect(screen, self.settings.WHITE, indicator_rect)
            
            screen.blit(text, rect)
        
        # Draw instructions
        instructions = [
            "Use ↑↓ to navigate",
            "Press ENTER to select",
            "Press ESC to resume"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, self.settings.DARK_GRAY)
            rect = text.get_rect(center=(self.settings.SCREEN_WIDTH // 2, 
                                       self.settings.SCREEN_HEIGHT - 100 + i * 30))
            screen.blit(text, rect)
