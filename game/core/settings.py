"""
Game settings and configuration
"""

import os
from dataclasses import dataclass

@dataclass
class Settings:
    """Game settings and configuration"""
    
    # Display settings
    SCREEN_WIDTH: int = 1200
    SCREEN_HEIGHT: int = 800
    FPS: int = 60
    TILE_SIZE: int = 32
    TITLE: str = "The Game - Roguelike Adventure"
    
    # Player settings
    PLAYER_SPEED: float = 200.0
    PLAYER_HEALTH: int = 100
    PLAYER_ATTACK_POWER: int = 15
    PLAYER_DEFENSE: int = 5
    
    # Enemy settings
    ENEMY_SPEED: float = 100.0
    ENEMY_HEALTH: int = 50
    ENEMY_ATTACK_POWER: int = 10
    ENEMY_DEFENSE: int = 2
    
    # Game settings
    DEBUG_MODE: bool = False
    GAME_MODE: str = "campaign"  # "campaign" or "open_world"
    MODE_CAMPAIGN: str = "campaign"
    MODE_OPEN_WORLD: str = "open_world"
    
    # Colors
    BLACK: tuple = (0, 0, 0)
    WHITE: tuple = (255, 255, 255)
    RED: tuple = (255, 0, 0)
    GREEN: tuple = (0, 255, 0)
    BLUE: tuple = (0, 0, 255)
    YELLOW: tuple = (255, 255, 0)
    GRAY: tuple = (128, 128, 128)
    LIGHT_GRAY: tuple = (200, 200, 200)
    DARK_GRAY: tuple = (64, 64, 64)
    
    # Asset paths
    ASSETS_DIR: str = "assets"
    SOUNDS_DIR: str = "assets/sounds"
    MUSIC_DIR: str = "assets/music"
    IMAGES_DIR: str = "assets/images"
    FONTS_DIR: str = "assets/fonts"
    
    def __post_init__(self):
        """Create asset directories if they don't exist"""
        os.makedirs(self.ASSETS_DIR, exist_ok=True)
        os.makedirs(self.SOUNDS_DIR, exist_ok=True)
        os.makedirs(self.MUSIC_DIR, exist_ok=True)
        os.makedirs(self.IMAGES_DIR, exist_ok=True)
        os.makedirs(self.FONTS_DIR, exist_ok=True)
