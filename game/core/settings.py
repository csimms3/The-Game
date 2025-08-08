"""
Game settings and configuration
"""

import os
from dataclasses import dataclass
from typing import Tuple

@dataclass
class Settings:
    """Game settings and configuration"""
    
    # Display settings
    SCREEN_WIDTH: int = 1280
    SCREEN_HEIGHT: int = 720
    FPS: int = 60
    TITLE: str = "The Game - Roguelike Adventure"
    
    # Game settings
    TILE_SIZE: int = 32
    PLAYER_SPEED: float = 3.0
    ENEMY_SPEED: float = 1.5
    
    # Colors
    BLACK: Tuple[int, int, int] = (0, 0, 0)
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    RED: Tuple[int, int, int] = (255, 0, 0)
    GREEN: Tuple[int, int, int] = (0, 255, 0)
    BLUE: Tuple[int, int, int] = (0, 0, 255)
    GRAY: Tuple[int, int, int] = (128, 128, 128)
    DARK_GRAY: Tuple[int, int, int] = (64, 64, 64)
    LIGHT_GRAY: Tuple[int, int, int] = (192, 192, 192)
    
    # Asset paths
    ASSETS_DIR: str = "assets"
    SPRITES_DIR: str = os.path.join(ASSETS_DIR, "sprites")
    SOUNDS_DIR: str = os.path.join(ASSETS_DIR, "sounds")
    MUSIC_DIR: str = os.path.join(ASSETS_DIR, "music")
    MAPS_DIR: str = os.path.join(ASSETS_DIR, "maps")
    
    # Game modes
    MODE_CAMPAIGN: str = "campaign"
    MODE_OPEN_WORLD: str = "open_world"
    
    def __post_init__(self):
        """Ensure directories exist"""
        for directory in [self.ASSETS_DIR, self.SPRITES_DIR, 
                         self.SOUNDS_DIR, self.MUSIC_DIR, self.MAPS_DIR]:
            os.makedirs(directory, exist_ok=True)
