"""
Menu state with modern UI design
"""

import pygame
from game.states.base_state import BaseState
from game.graphics.ui_system import UISystem

class MenuState(BaseState):
    """Main menu state with modern design"""
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        
        # UI system
        self.ui_system = UISystem(self.settings)
        
        # Menu state
        self.selected_option = 0
        self.options = ["Campaign", "Open World", "Settings", "Quit"]
        
        # Animation
        self.title_y = -100
        self.title_target_y = 100
        self.animation_speed = 5
        
        # Visual effects
        self.background_particles = []
        self._create_background_particles()
    
    def _create_background_particles(self):
        """Create floating background particles"""
        import random
        for _ in range(20):
            self.background_particles.append({
                'x': random.randint(0, self.settings.SCREEN_WIDTH),
                'y': random.randint(0, self.settings.SCREEN_HEIGHT),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'size': random.randint(2, 6),
                'alpha': random.randint(50, 150)
            })
    
    def enter(self):
        """Called when entering menu state"""
        self.logger.info("Entering menu state")
        self.selected_option = 0
    
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
    
    def update(self, dt: float):
        """Update menu animations"""
        # Animate title
        if self.title_y < self.title_target_y:
            self.title_y += self.animation_speed * dt * 60
        
        # Update background particles
        for particle in self.background_particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = self.settings.SCREEN_WIDTH
            elif particle['x'] > self.settings.SCREEN_WIDTH:
                particle['x'] = 0
            
            if particle['y'] < 0:
                particle['y'] = self.settings.SCREEN_HEIGHT
            elif particle['y'] > self.settings.SCREEN_HEIGHT:
                particle['y'] = 0
    
    def render(self, screen):
        """Render the menu with modern design"""
        # Render background particles
        self._render_background_particles(screen)
        
        # Render main menu using UI system
        self.ui_system.render_main_menu(screen, self.selected_option)
    
    def _render_background_particles(self, screen):
        """Render floating background particles"""
        for particle in self.background_particles:
            particle_surface = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (100, 150, 255, particle['alpha']), 
                             (particle['size'] // 2, particle['size'] // 2), particle['size'] // 2)
            screen.blit(particle_surface, (particle['x'], particle['y']))
    
    def _select_option(self):
        """Handle option selection"""
        if self.selected_option == 0:  # Campaign
            self.game_engine.game_mode = "campaign"
            self.game_engine.change_state('game')
        elif self.selected_option == 1:  # Open World
            self.game_engine.game_mode = "open_world"
            self.game_engine.change_state('game')
        elif self.selected_option == 2:  # Settings
            # TODO: Implement settings menu
            pass
        elif self.selected_option == 3:  # Quit
            self.game_engine.quit()
