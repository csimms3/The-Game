"""
Sound and music management system
"""

import pygame
import os
import random
from typing import Dict, List, Optional, Any
from game.core.settings import Settings

class SoundManager:
    """Manages all audio in the game"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: List[str] = []
        self.current_music = None
        self.volume = 0.7
        self.music_volume = 0.5
        
        # Audio settings
        self.sound_enabled = True
        self.music_enabled = True
        
        # Initialize audio
        self._initialize_audio()
    
    def _initialize_audio(self):
        """Initialize audio system and load sounds"""
        # Create sounds directory if it doesn't exist
        os.makedirs(self.settings.SOUNDS_DIR, exist_ok=True)
        os.makedirs(self.settings.MUSIC_DIR, exist_ok=True)
        
        # Generate placeholder sounds (since we don't have actual audio files)
        self._create_placeholder_sounds()
    
    def _create_placeholder_sounds(self):
        """Create placeholder sounds using pygame's audio generation"""
        # This is a placeholder - in a real game you'd load actual sound files
        # For now, we'll create simple tones for different effects
        
        # Combat sounds
        self._create_tone_sound("attack", 440, 0.1)  # A note
        self._create_tone_sound("hit", 220, 0.2)     # Low note
        self._create_tone_sound("damage", 880, 0.15) # High note
        self._create_tone_sound("heal", 330, 0.3)    # E note
        
        # UI sounds
        self._create_tone_sound("menu_select", 660, 0.05)
        self._create_tone_sound("menu_confirm", 880, 0.1)
        self._create_tone_sound("item_pickup", 550, 0.1)
        self._create_tone_sound("level_up", 1100, 0.5)
        
        # Environment sounds
        self._create_tone_sound("footstep", 100, 0.05)
        self._create_tone_sound("enemy_death", 150, 0.3)
        self._create_tone_sound("explosion", 50, 0.4)
    
    def _create_tone_sound(self, name: str, frequency: int, duration: float):
        """Create a simple tone sound"""
        try:
            # Generate a simple sine wave tone
            sample_rate = 44100
            samples = int(sample_rate * duration)
            
            # Create a simple tone (sine wave)
            import math
            import numpy as np
            
            # Generate sine wave
            t = np.linspace(0, duration, samples, False)
            tone = np.sin(2 * np.pi * frequency * t)
            
            # Convert to 16-bit integer
            tone = (tone * 32767).astype(np.int16)
            
            # Create stereo array (2D array for left and right channels)
            stereo_tone = np.column_stack((tone, tone))
            
            # Create pygame sound from stereo array
            sound = pygame.sndarray.make_sound(stereo_tone)
            
            self.sounds[name] = sound
        except Exception as e:
            print(f"Could not create sound {name}: {e}")
    
    def play_sound(self, sound_name: str, volume: float = None):
        """Play a sound effect"""
        if not self.sound_enabled or sound_name not in self.sounds:
            return
        
        try:
            sound = self.sounds[sound_name]
            if volume is None:
                volume = self.volume
            
            sound.set_volume(volume)
            sound.play()
        except Exception as e:
            print(f"Error playing sound {sound_name}: {e}")
    
    def play_music(self, track_name: str, loop: bool = True):
        """Play background music"""
        if not self.music_enabled:
            return
        
        try:
            # In a real implementation, you'd load actual music files
            # For now, we'll just track what music should be playing
            self.current_music = track_name
            
            # Placeholder for music loading
            # pygame.mixer.music.load(os.path.join(self.settings.MUSIC_DIR, track_name))
            # pygame.mixer.music.set_volume(self.music_volume)
            # pygame.mixer.music.play(-1 if loop else 0)
            
        except Exception as e:
            print(f"Error playing music {track_name}: {e}")
    
    def stop_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
            self.current_music = None
        except Exception as e:
            print(f"Error stopping music: {e}")
    
    def pause_music(self):
        """Pause background music"""
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"Error pausing music: {e}")
    
    def unpause_music(self):
        """Unpause background music"""
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Error unpausing music: {e}")
    
    def set_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception as e:
            print(f"Error setting music volume: {e}")
    
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        self.sound_enabled = not self.sound_enabled
    
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
    
    def play_combat_sounds(self, action: str):
        """Play appropriate combat sounds"""
        if action == "attack":
            self.play_sound("attack")
        elif action == "hit":
            self.play_sound("hit")
        elif action == "damage":
            self.play_sound("damage")
        elif action == "heal":
            self.play_sound("heal")
        elif action == "enemy_death":
            self.play_sound("enemy_death")
    
    def play_ui_sounds(self, action: str):
        """Play UI interaction sounds"""
        if action == "select":
            self.play_sound("menu_select")
        elif action == "confirm":
            self.play_sound("menu_confirm")
        elif action == "pickup":
            self.play_sound("item_pickup")
        elif action == "level_up":
            self.play_sound("level_up")
    
    def play_ambient_sounds(self, action: str):
        """Play ambient/environment sounds"""
        if action == "footstep":
            self.play_sound("footstep", 0.3)
        elif action == "explosion":
            self.play_sound("explosion")
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """Get current audio settings"""
        return {
            'sound_enabled': self.sound_enabled,
            'music_enabled': self.music_enabled,
            'volume': self.volume,
            'music_volume': self.music_volume,
            'current_music': self.current_music
        }
    
    def set_audio_settings(self, settings: Dict[str, Any]):
        """Set audio settings"""
        if 'sound_enabled' in settings:
            self.sound_enabled = settings['sound_enabled']
        if 'music_enabled' in settings:
            self.music_enabled = settings['music_enabled']
        if 'volume' in settings:
            self.set_volume(settings['volume'])
        if 'music_volume' in settings:
            self.set_music_volume(settings['music_volume'])
