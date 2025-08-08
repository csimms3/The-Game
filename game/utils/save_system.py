"""
Save and load system for game state
"""

import json
import os
import pickle
from datetime import datetime
from typing import Dict, Any, Optional, List
from game.core.settings import Settings

class SaveSystem:
    """Handles saving and loading game state"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.save_dir = "saves"
        os.makedirs(self.save_dir, exist_ok=True)
    
    def save_game(self, game_state, filename: str = None) -> bool:
        """Save game state to file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"save_{timestamp}.json"
            
            save_data = self._serialize_game_state(game_state)
            
            filepath = os.path.join(self.save_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load game state from file"""
        try:
            filepath = os.path.join(self.save_dir, filename)
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            return save_data
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def get_save_files(self) -> List[str]:
        """Get list of available save files"""
        if not os.path.exists(self.save_dir):
            return []
        
        save_files = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json'):
                save_files.append(filename)
        
        return sorted(save_files, reverse=True)
    
    def delete_save(self, filename: str) -> bool:
        """Delete a save file"""
        try:
            filepath = os.path.join(self.save_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
    
    def _serialize_game_state(self, game_state) -> Dict[str, Any]:
        """Serialize game state for saving"""
        save_data = {
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'player': {
                'x': game_state.player.x,
                'y': game_state.player.y,
                'health': game_state.player.health,
                'max_health': game_state.player.max_health,
                'level': game_state.player.level,
                'experience': game_state.player.experience,
                'experience_to_next_level': game_state.player.experience_to_next_level,
                'attack_power': game_state.player.attack_power,
                'defense': game_state.player.defense,
                'speed': game_state.player.speed,
                'inventory': [item.name for item in game_state.player.inventory],
                'equipped_weapon': game_state.player.equipped_weapon.name if game_state.player.equipped_weapon else None,
                'equipped_armor': game_state.player.equipped_armor.name if game_state.player.equipped_armor else None
            },
            'game_state': {
                'game_mode': game_state.game_mode,
                'game_time': game_state.game_time,
                'score': game_state.score,
                'camera_x': game_state.camera_x,
                'camera_y': game_state.camera_y
            },
            'world': {
                'seed': game_state.world_generator.seed,
                'items': [
                    {
                        'x': item['x'],
                        'y': item['y'],
                        'item_name': item['item'].name
                    }
                    for item in game_state.items
                ]
            },
            'enemies': [
                {
                    'x': enemy.x,
                    'y': enemy.y,
                    'enemy_type': enemy.enemy_type,
                    'health': enemy.health,
                    'alive': enemy.alive
                }
                for enemy in game_state.enemies if enemy.alive
            ],
            'messages': game_state.messages
        }
        
        return save_data
    
    def _deserialize_game_state(self, save_data: Dict[str, Any], game_state):
        """Deserialize game state from save data"""
        try:
            # Restore player data
            player_data = save_data['player']
            game_state.player.x = player_data['x']
            game_state.player.y = player_data['y']
            game_state.player.health = player_data['health']
            game_state.player.max_health = player_data['max_health']
            game_state.player.level = player_data['level']
            game_state.player.experience = player_data['experience']
            game_state.player.experience_to_next_level = player_data['experience_to_next_level']
            game_state.player.attack_power = player_data['attack_power']
            game_state.player.defense = player_data['defense']
            game_state.player.speed = player_data['speed']
            
            # Restore game state
            state_data = save_data['game_state']
            game_state.game_mode = state_data['game_mode']
            game_state.game_time = state_data['game_time']
            game_state.score = state_data['score']
            game_state.camera_x = state_data['camera_x']
            game_state.camera_y = state_data['camera_y']
            
            # Restore messages
            game_state.messages = save_data.get('messages', [])
            
            return True
        except Exception as e:
            print(f"Error deserializing game state: {e}")
            return False
    
    def get_save_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get information about a save file"""
        try:
            filepath = os.path.join(self.save_dir, filename)
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Get file stats
            stat = os.stat(filepath)
            
            return {
                'filename': filename,
                'timestamp': save_data.get('timestamp', ''),
                'version': save_data.get('version', ''),
                'player_level': save_data.get('player', {}).get('level', 1),
                'game_mode': save_data.get('game_state', {}).get('game_mode', ''),
                'score': save_data.get('game_state', {}).get('score', 0),
                'file_size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except Exception as e:
            print(f"Error getting save info: {e}")
            return None
