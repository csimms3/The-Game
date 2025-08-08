"""
Pause state with modern UI design
"""

import pygame
from game.states.base_state import BaseState
from game.graphics.ui_system import UISystem

class PauseState(BaseState):
    """Pause menu state with modern design"""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        
        # UI system
        self.ui_system = UISystem(self.settings)
        
        # Pause state
        self.selected_option = 0
        self.options = ["Resume", "Settings", "Main Menu", "Quit"]
        
        # Visual effects
        self.blur_strength = 0
        self.target_blur = 50
    
    def enter(self):
        """Called when entering pause state"""
        self.logger.info("Entering pause state")
        self.selected_option = 0
        self.blur_strength = 0
    
    def exit(self):
        """Called when exiting pause state"""
        self.logger.info("Exiting pause state")
    
    def handle_event(self, event):
        """Handle pause menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_engine.change_state('game')
            elif event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._select_option()
    
    def update(self, dt: float):
        """Update pause state animations"""
        # Animate blur effect
        if self.blur_strength < self.target_blur:
            self.blur_strength += 5 * dt * 60
    
    def render(self, screen):
        """Render the pause menu with modern design"""
        # Apply blur effect to background
        if self.blur_strength > 0:
            blur_surface = screen.copy()
            blur_surface.set_alpha(int(self.blur_strength))
            screen.blit(blur_surface, (0, 0))
        
        # Render pause menu using UI system
        self.ui_system.render_pause_menu(screen, self.selected_option)
    
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
