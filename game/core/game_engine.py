"""
Main game engine
"""

import pygame
import sys
from typing import Optional
from game.core.settings import Settings
from game.states.menu_state import MenuState
from game.states.game_state import GameState
from game.states.pause_state import PauseState
from game.utils.logger import setup_logger

class GameEngine:
    """Main game engine class"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = setup_logger()
        
        # Initialize display
        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        
        # Game states
        self.states = {
            'menu': MenuState(self),
            'game': GameState(self),
            'pause': PauseState(self)
        }
        self.current_state = 'menu'
        
        # Game flags
        self.running = True
        self.game_mode = None
        
        self.logger.info("Game engine initialized")
    
    def run(self):
        """Main game loop"""
        self.logger.info("Starting game loop")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.settings.FPS) / 1000.0  # Convert to seconds
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.states[self.current_state].handle_event(event)
            
            # Update current state
            self.states[self.current_state].update(dt)
            
            # Render current state
            self.screen.fill(self.settings.BLACK)
            self.states[self.current_state].render(self.screen)
            
            # Update display
            pygame.display.flip()
        
        self.logger.info("Game loop ended")
    
    def change_state(self, state_name: str):
        """Change to a different game state"""
        if state_name in self.states:
            self.logger.info(f"Changing state from {self.current_state} to {state_name}")
            self.current_state = state_name
            self.states[state_name].enter()
        else:
            self.logger.error(f"Unknown state: {state_name}")
    
    def quit(self):
        """Quit the game"""
        self.running = False
