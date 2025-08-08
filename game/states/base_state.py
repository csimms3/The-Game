"""
Base state class for all game states
"""

import pygame
from abc import ABC, abstractmethod
from typing import Optional

class BaseState(ABC):
    """Base class for all game states"""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.settings = game_engine.settings
        self.logger = game_engine.logger
    
    @abstractmethod
    def enter(self):
        """Called when entering this state"""
        pass
    
    @abstractmethod
    def exit(self):
        """Called when exiting this state"""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """Update state logic"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Render the state"""
        pass
