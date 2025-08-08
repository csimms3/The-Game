#!/usr/bin/env python3
"""
The Game - A Roguelike Adventure
Main entry point for the game
"""

import sys
import os
import pygame
from game.core.game_engine import GameEngine
from game.core.settings import Settings
from game.utils.logger import setup_logger

def main():
    """Main game entry point"""
    # Setup logging
    logger = setup_logger()
    logger.info("Starting The Game - Roguelike Adventure")
    
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()
    
    # Create settings
    settings = Settings()
    
    # Create and run game engine
    game = GameEngine(settings)
    
    try:
        game.run()
    except Exception as e:
        logger.error(f"Game crashed with error: {e}")
        raise
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
