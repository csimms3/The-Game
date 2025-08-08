"""
Advanced enemy types with special abilities
"""

import pygame
import math
import random
from typing import List, Tuple, Optional
from game.entities.enemy import Enemy
from game.core.settings import Settings

class BossEnemy(Enemy):
    """Boss enemy with special abilities"""
    
    def __init__(self, x: float, y: float, settings: Settings, boss_type: str = "dragon"):
        super().__init__(x, y, settings, boss_type)
        
        self.boss_type = boss_type
        self.is_boss = True
        
        # Boss specific stats
        self.max_health = 500
        self.health = self.max_health
        self.attack_power = 25
        self.defense = 15
        self.speed = settings.ENEMY_SPEED * 0.8
        
        # Special abilities
        self.ability_cooldown = 0
        self.ability_timer = 0
        self.rage_mode = False
        self.rage_threshold = 0.3  # Enter rage mode at 30% health
        
        # Boss abilities
        self.abilities = self._get_boss_abilities()
        
        # Visual effects
        self.aura_color = (255, 0, 0)  # Red aura for boss
        self.aura_timer = 0
        
        self._create_boss_sprite()
    
    def _get_boss_abilities(self) -> List[str]:
        """Get boss abilities based on type"""
        if self.boss_type == "dragon":
            return ["fire_breath", "wing_slam", "roar"]
        elif self.boss_type == "lich":
            return ["summon_skeletons", "death_bolt", "fear"]
        elif self.boss_type == "golem":
            return ["rock_throw", "earthquake", "regeneration"]
        else:
            return ["power_strike", "charge", "heal"]
    
    def _create_boss_sprite(self):
        """Create boss sprite"""
        self.sprite = pygame.Surface((self.width * 2, self.height * 2))  # Bosses are bigger
        
        if self.boss_type == "dragon":
            self.sprite.fill((139, 0, 0))  # Dark red
        elif self.boss_type == "lich":
            self.sprite.fill((128, 128, 128))  # Gray
        elif self.boss_type == "golem":
            self.sprite.fill((105, 105, 105))  # Dark gray
        else:
            self.sprite.fill((255, 0, 0))  # Red
        
        # Add boss details
        pygame.draw.rect(self.sprite, (255, 255, 255), 
                        (4, 4, self.width * 2 - 8, self.height * 2 - 8))
        
        # Add crown or special marking
        crown_rect = pygame.Rect(self.width - 8, 4, 16, 8)
        pygame.draw.rect(self.sprite, (255, 215, 0), crown_rect)  # Gold crown
    
    def update(self, dt: float):
        """Update boss AI and abilities"""
        super().update(dt)
        
        # Update ability timers
        if self.ability_cooldown > 0:
            self.ability_cooldown -= dt
        
        # Check for rage mode
        if self.health / self.max_health <= self.rage_threshold and not self.rage_mode:
            self._enter_rage_mode()
        
        # Update aura effect
        self.aura_timer += dt
        
        # Use abilities
        if self.ability_cooldown <= 0 and self.target:
            self._use_ability()
    
    def _enter_rage_mode(self):
        """Enter rage mode when health is low"""
        self.rage_mode = True
        self.attack_power *= 1.5
        self.speed *= 1.2
        self.aura_color = (255, 255, 0)  # Yellow aura in rage mode
    
    def _use_ability(self):
        """Use a random boss ability"""
        if not self.abilities:
            return
        
        ability = random.choice(self.abilities)
        
        if ability == "fire_breath":
            self._fire_breath_ability()
        elif ability == "wing_slam":
            self._wing_slam_ability()
        elif ability == "roar":
            self._roar_ability()
        elif ability == "summon_skeletons":
            self._summon_skeletons_ability()
        elif ability == "death_bolt":
            self._death_bolt_ability()
        elif ability == "rock_throw":
            self._rock_throw_ability()
        elif ability == "earthquake":
            self._earthquake_ability()
        else:
            self._power_strike_ability()
        
        # Set cooldown
        self.ability_cooldown = random.uniform(3.0, 8.0)
    
    def _fire_breath_ability(self):
        """Dragon fire breath ability"""
        if self.target:
            # Create fire breath effect
            damage = 30
            self.target.take_damage(damage)
            # TODO: Create fire breath visual effect
    
    def _wing_slam_ability(self):
        """Dragon wing slam ability"""
        # Area attack
        if self.target:
            distance = self.distance_to(self.target)
            if distance <= 100:
                damage = 25
                self.target.take_damage(damage)
    
    def _roar_ability(self):
        """Dragon roar ability"""
        # Fear effect - temporarily reduce target stats
        if self.target:
            # TODO: Implement fear debuff
            pass
    
    def _summon_skeletons_ability(self):
        """Lich summon skeletons ability"""
        # TODO: Create skeleton minions
        pass
    
    def _death_bolt_ability(self):
        """Lich death bolt ability"""
        if self.target:
            damage = 35
            self.target.take_damage(damage)
    
    def _rock_throw_ability(self):
        """Golem rock throw ability"""
        if self.target:
            damage = 20
            self.target.take_damage(damage)
    
    def _earthquake_ability(self):
        """Golem earthquake ability"""
        # Area damage
        if self.target:
            distance = self.distance_to(self.target)
            if distance <= 150:
                damage = 30
                self.target.take_damage(damage)
    
    def _power_strike_ability(self):
        """Generic power strike ability"""
        if self.target:
            damage = 40
            self.target.take_damage(damage)
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render boss with aura effect"""
        if not self.visible or not self.alive:
            return
        
        # Calculate screen position
        screen_x = self.x - camera_offset[0]
        screen_y = self.y - camera_offset[1]
        
        # Draw aura effect
        aura_size = int(8 * math.sin(self.aura_timer * 3) + 12)
        aura_surface = pygame.Surface((self.width * 2 + aura_size * 2, 
                                     self.height * 2 + aura_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, (*self.aura_color, 100), 
                         (self.width + aura_size, self.height + aura_size), aura_size)
        screen.blit(aura_surface, (screen_x - aura_size, screen_y - aura_size))
        
        # Draw boss sprite
        screen.blit(self.sprite, (screen_x, screen_y))
        
        # Draw boss health bar
        self._draw_boss_health_bar(screen, screen_x, screen_y)
    
    def _draw_boss_health_bar(self, screen: pygame.Surface, x: float, y: float):
        """Draw boss health bar"""
        bar_width = self.width * 2
        bar_height = 8
        bar_y = y - 20
        
        # Background
        pygame.draw.rect(screen, (100, 20, 20), 
                        (x, bar_y, bar_width, bar_height))
        
        # Health
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        health_color = (255, 50, 50) if not self.rage_mode else (255, 255, 0)
        pygame.draw.rect(screen, health_color, 
                        (x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), 
                        (x, bar_y, bar_width, bar_height), 2)
        
        # Boss name
        font = pygame.font.Font(None, 24)
        name_text = font.render(f"BOSS: {self.boss_type.title()}", True, (255, 255, 255))
        screen.blit(name_text, (x, bar_y - 20))

class EliteEnemy(Enemy):
    """Elite enemy with enhanced abilities"""
    
    def __init__(self, x: float, y: float, settings: Settings, elite_type: str = "warrior"):
        super().__init__(x, y, settings, elite_type)
        
        self.elite_type = elite_type
        
        # Enhanced stats
        self.max_health = 200
        self.health = self.max_health
        self.attack_power = 18
        self.defense = 10
        self.speed = settings.ENEMY_SPEED * 1.1
        
        # Elite abilities
        self.special_ability = self._get_elite_ability()
        self.ability_cooldown = 0
        
        # Visual indicator
        self.elite_glow = 0
        
        self._create_elite_sprite()
    
    def _get_elite_ability(self) -> str:
        """Get elite ability based on type"""
        abilities = {
            "warrior": "shield_bash",
            "archer": "rapid_shot",
            "mage": "fireball",
            "assassin": "stealth_strike"
        }
        return abilities.get(self.elite_type, "power_strike")
    
    def _create_elite_sprite(self):
        """Create elite enemy sprite"""
        self.sprite = pygame.Surface((self.width, self.height))
        
        # Elite color coding
        colors = {
            "warrior": (139, 69, 19),  # Brown
            "archer": (0, 100, 0),     # Dark green
            "mage": (75, 0, 130),      # Indigo
            "assassin": (47, 79, 79)   # Dark slate
        }
        
        color = colors.get(self.elite_type, (128, 128, 128))
        self.sprite.fill(color)
        
        # Add elite marking
        pygame.draw.rect(self.sprite, (255, 215, 0), (2, 2, self.width - 4, 4))  # Gold stripe
    
    def update(self, dt: float):
        """Update elite enemy"""
        super().update(dt)
        
        # Update ability cooldown
        if self.ability_cooldown > 0:
            self.ability_cooldown -= dt
        
        # Update glow effect
        self.elite_glow += dt * 2
        
        # Use special ability
        if self.ability_cooldown <= 0 and self.target:
            self._use_elite_ability()
    
    def _use_elite_ability(self):
        """Use elite special ability"""
        if self.special_ability == "shield_bash":
            self._shield_bash_ability()
        elif self.special_ability == "rapid_shot":
            self._rapid_shot_ability()
        elif self.special_ability == "fireball":
            self._fireball_ability()
        elif self.special_ability == "stealth_strike":
            self._stealth_strike_ability()
        
        self.ability_cooldown = random.uniform(2.0, 5.0)
    
    def _shield_bash_ability(self):
        """Warrior shield bash ability"""
        if self.target:
            damage = 15
            self.target.take_damage(damage)
            # TODO: Add stun effect
    
    def _rapid_shot_ability(self):
        """Archer rapid shot ability"""
        if self.target:
            # Multiple quick attacks
            for _ in range(3):
                damage = 8
                self.target.take_damage(damage)
    
    def _fireball_ability(self):
        """Mage fireball ability"""
        if self.target:
            damage = 25
            self.target.take_damage(damage)
            # TODO: Add burning effect
    
    def _stealth_strike_ability(self):
        """Assassin stealth strike ability"""
        if self.target:
            damage = 30
            self.target.take_damage(damage)
            # TODO: Add critical hit effect
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render elite enemy with glow effect"""
        if not self.visible or not self.alive:
            return
        
        # Calculate screen position
        screen_x = self.x - camera_offset[0]
        screen_y = self.y - camera_offset[1]
        
        # Draw glow effect
        glow_size = int(4 * math.sin(self.elite_glow) + 6)
        glow_surface = pygame.Surface((self.width + glow_size * 2, 
                                     self.height + glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 215, 0, 80), 
                         (self.width // 2 + glow_size, self.height // 2 + glow_size), glow_size)
        screen.blit(glow_surface, (screen_x - glow_size, screen_y - glow_size))
        
        # Draw elite sprite
        screen.blit(self.sprite, (screen_x, screen_y))
        
        # Draw elite health bar
        self._draw_elite_health_bar(screen, screen_x, screen_y)
    
    def _draw_elite_health_bar(self, screen: pygame.Surface, x: float, y: float):
        """Draw elite health bar"""
        bar_width = self.width
        bar_height = 6
        bar_y = y - 12
        
        # Background
        pygame.draw.rect(screen, (100, 20, 20), 
                        (x, bar_y, bar_width, bar_height))
        
        # Health
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, (255, 215, 0), 
                        (x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), 
                        (x, bar_y, bar_width, bar_height), 1)
