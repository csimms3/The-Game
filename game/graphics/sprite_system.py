"""
Advanced sprite system with custom graphics and animations
"""

import pygame
import math
import random
from typing import Dict, List, Tuple, Optional
from game.core.settings import Settings

class SpriteSheet:
    """Manages sprite sheets and individual sprites"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.sprites: Dict[str, pygame.Surface] = {}
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self._create_custom_sprites()
    
    def _create_custom_sprites(self):
        """Create custom sprites with refined graphics"""
        # Player sprites
        self._create_player_sprites()
        
        # Enemy sprites
        self._create_enemy_sprites()
        
        # Environment sprites
        self._create_environment_sprites()
        
        # UI sprites
        self._create_ui_sprites()
        
        # Effect sprites
        self._create_effect_sprites()
    
    def _create_player_sprites(self):
        """Create sophisticated player sprites"""
        # Player base sprite (32x32)
        player_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        # Body (dark blue)
        pygame.draw.circle(player_sprite, (30, 60, 120), (16, 20), 8)
        
        # Head (light blue)
        pygame.draw.circle(player_sprite, (80, 140, 200), (16, 12), 6)
        
        # Eyes (white with black pupils)
        pygame.draw.circle(player_sprite, (255, 255, 255), (14, 10), 2)
        pygame.draw.circle(player_sprite, (255, 255, 255), (18, 10), 2)
        pygame.draw.circle(player_sprite, (0, 0, 0), (14, 10), 1)
        pygame.draw.circle(player_sprite, (0, 0, 0), (18, 10), 1)
        
        # Equipment glow
        pygame.draw.circle(player_sprite, (100, 200, 255, 50), (16, 16), 12, 2)
        
        self.sprites["player"] = player_sprite
        
        # Player attack animation
        attack_frames = []
        for i in range(4):
            frame = player_sprite.copy()
            # Add attack effect
            angle = i * 45
            end_x = 16 + math.cos(math.radians(angle)) * 20
            end_y = 16 + math.sin(math.radians(angle)) * 20
            pygame.draw.line(frame, (255, 255, 0), (16, 16), (end_x, end_y), 3)
            attack_frames.append(frame)
        
        self.animations["player_attack"] = attack_frames
    
    def _create_enemy_sprites(self):
        """Create diverse enemy sprites"""
        # Goblin sprite
        goblin = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(goblin, (100, 150, 50), (12, 16), 6)  # Body
        pygame.draw.circle(goblin, (150, 200, 100), (12, 8), 4)   # Head
        pygame.draw.circle(goblin, (255, 0, 0), (10, 7), 1)       # Red eyes
        pygame.draw.circle(goblin, (255, 0, 0), (14, 7), 1)
        self.sprites["goblin"] = goblin
        
        # Orc sprite
        orc = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(orc, (80, 120, 80), (14, 18), 8)       # Body
        pygame.draw.circle(orc, (120, 160, 120), (14, 10), 5)      # Head
        pygame.draw.circle(orc, (200, 0, 0), (12, 9), 1)          # Red eyes
        pygame.draw.circle(orc, (200, 0, 0), (16, 9), 1)
        self.sprites["orc"] = orc
        
        # Skeleton sprite
        skeleton = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(skeleton, (200, 200, 200), (12, 16), 6) # Body
        pygame.draw.circle(skeleton, (240, 240, 240), (12, 8), 4)   # Head
        pygame.draw.circle(skeleton, (0, 0, 0), (10, 7), 1)        # Black eyes
        pygame.draw.circle(skeleton, (0, 0, 0), (14, 7), 1)
        self.sprites["skeleton"] = skeleton
        
        # Boss sprites
        self._create_boss_sprites()
        
        # Elite sprites
        self._create_elite_sprites()
    
    def _create_boss_sprites(self):
        """Create impressive boss sprites"""
        # Dragon boss (64x64)
        dragon = pygame.Surface((64, 64), pygame.SRCALPHA)
        
        # Dragon body (red gradient)
        for i in range(8):
            color = (150 + i * 10, 50 + i * 5, 50 + i * 5)
            pygame.draw.circle(dragon, color, (32, 40 - i * 2), 12 - i)
        
        # Dragon head
        pygame.draw.circle(dragon, (200, 100, 100), (32, 20), 8)
        pygame.draw.circle(dragon, (255, 0, 0), (30, 18), 2)  # Red eyes
        pygame.draw.circle(dragon, (255, 0, 0), (34, 18), 2)
        
        # Wings
        pygame.draw.ellipse(dragon, (180, 80, 80), (10, 25, 20, 15))
        pygame.draw.ellipse(dragon, (180, 80, 80), (34, 25, 20, 15))
        
        # Fire breath effect
        pygame.draw.polygon(dragon, (255, 100, 0), [(28, 15), (40, 10), (35, 20)])
        
        self.sprites["dragon"] = dragon
        
        # Lich boss
        lich = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(lich, (100, 100, 150), (24, 30), 10)  # Body
        pygame.draw.circle(lich, (150, 150, 200), (24, 15), 8)    # Head
        pygame.draw.circle(lich, (0, 255, 255), (22, 13), 2)      # Cyan eyes
        pygame.draw.circle(lich, (0, 255, 255), (26, 13), 2)
        
        # Magic aura
        for i in range(3):
            pygame.draw.circle(lich, (0, 255, 255, 50 - i * 15), (24, 24), 20 - i * 5)
        
        self.sprites["lich"] = lich
    
    def _create_elite_sprites(self):
        """Create elite enemy sprites with special effects"""
        # Elite warrior
        warrior = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(warrior, (120, 80, 40), (16, 20), 8)   # Body
        pygame.draw.circle(warrior, (160, 120, 80), (16, 10), 6)   # Head
        pygame.draw.circle(warrior, (255, 215, 0), (14, 8), 1)     # Gold eyes
        pygame.draw.circle(warrior, (255, 215, 0), (18, 8), 1)
        
        # Golden armor glow
        pygame.draw.circle(warrior, (255, 215, 0, 100), (16, 16), 16, 2)
        
        self.sprites["elite_warrior"] = warrior
    
    def _create_environment_sprites(self):
        """Create beautiful environment sprites"""
        # Grass tile
        grass = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(grass, (50, 150, 50), (0, 0, 32, 32))
        # Add grass details
        for i in range(8):
            x = random.randint(4, 28)
            y = random.randint(4, 28)
            pygame.draw.line(grass, (100, 200, 100), (x, y), (x, y - 4), 1)
        self.sprites["grass"] = grass
        
        # Forest tile
        forest = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(forest, (30, 100, 30), (0, 0, 32, 32))
        # Add tree details
        pygame.draw.circle(forest, (80, 120, 80), (16, 8), 6)
        pygame.draw.rect(forest, (100, 60, 30), (15, 16, 2, 8))
        self.sprites["forest"] = forest
        
        # Water tile
        water = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(water, (50, 100, 200), (0, 0, 32, 32))
        # Add wave effect
        for i in range(4):
            y = 8 + i * 6
            pygame.draw.line(water, (100, 150, 255), (0, y), (32, y), 1)
        self.sprites["water"] = water
        
        # Mountain tile
        mountain = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.polygon(mountain, (120, 120, 120), [(0, 32), (16, 8), (32, 32)])
        pygame.draw.polygon(mountain, (100, 100, 100), [(8, 32), (16, 12), (24, 32)])
        self.sprites["mountain"] = mountain
    
    def _create_ui_sprites(self):
        """Create refined UI sprites"""
        # Health bar background
        health_bg = pygame.Surface((100, 12), pygame.SRCALPHA)
        pygame.draw.rect(health_bg, (60, 60, 60), (0, 0, 100, 12))
        pygame.draw.rect(health_bg, (40, 40, 40), (0, 0, 100, 12), 2)
        self.sprites["health_bg"] = health_bg
        
        # Health bar fill
        health_fill = pygame.Surface((100, 12), pygame.SRCALPHA)
        pygame.draw.rect(health_fill, (255, 50, 50), (0, 0, 100, 12))
        self.sprites["health_fill"] = health_fill
        
        # Experience bar
        exp_bg = pygame.Surface((100, 8), pygame.SRCALPHA)
        pygame.draw.rect(exp_bg, (40, 40, 60), (0, 0, 100, 8))
        pygame.draw.rect(exp_bg, (30, 30, 50), (0, 0, 100, 8), 1)
        self.sprites["exp_bg"] = exp_bg
        
        exp_fill = pygame.Surface((100, 8), pygame.SRCALPHA)
        pygame.draw.rect(exp_fill, (100, 200, 255), (0, 0, 100, 8))
        self.sprites["exp_fill"] = exp_fill
    
    def _create_effect_sprites(self):
        """Create visual effect sprites"""
        # Damage effect
        damage = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(damage, (255, 0, 0), (8, 8), 6)
        pygame.draw.circle(damage, (255, 100, 100), (8, 8), 4)
        self.sprites["damage"] = damage
        
        # Heal effect
        heal = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(heal, (0, 255, 0), (8, 8), 6)
        pygame.draw.circle(heal, (100, 255, 100), (8, 8), 4)
        self.sprites["heal"] = heal
        
        # Level up effect
        level_up = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(level_up, (255, 255, 0), (12, 12), 10)
        pygame.draw.circle(level_up, (255, 255, 100), (12, 12), 6)
        self.sprites["level_up"] = level_up
    
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name"""
        return self.sprites.get(name)
    
    def get_animation(self, name: str) -> Optional[List[pygame.Surface]]:
        """Get an animation by name"""
        return self.animations.get(name)
    
    def create_animated_sprite(self, base_name: str, animation_frames: int) -> List[pygame.Surface]:
        """Create an animated sprite from a base sprite"""
        base_sprite = self.get_sprite(base_name)
        if not base_sprite:
            return []
        
        frames = []
        for i in range(animation_frames):
            frame = base_sprite.copy()
            # Add subtle animation effects
            if i % 2 == 0:
                # Slight glow effect
                glow = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 255, 255, 30), 
                                (frame.get_width() // 2, frame.get_height() // 2), 
                                frame.get_width() // 2)
                frame.blit(glow, (0, 0))
            frames.append(frame)
        
        return frames
