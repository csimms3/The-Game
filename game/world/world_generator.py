"""
World generation system
"""

import pygame
import random
import noise
import math
from typing import List, Tuple, Dict, Any
from game.core.settings import Settings
from game.items.item import ItemFactory

class WorldGenerator:
    """Generates procedural worlds"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.seed = random.randint(0, 1000000)
        self.world_width = 2000
        self.world_height = 2000
        self.tile_size = settings.TILE_SIZE
        
        # Terrain types
        self.terrain_types = {
            'grass': {'color': (34, 139, 34), 'walkable': True, 'movement_cost': 1},
            'forest': {'color': (0, 100, 0), 'walkable': True, 'movement_cost': 1.5},
            'water': {'color': (0, 105, 148), 'walkable': False, 'movement_cost': 0},
            'mountain': {'color': (139, 137, 137), 'walkable': True, 'movement_cost': 2},
            'desert': {'color': (238, 203, 173), 'walkable': True, 'movement_cost': 1.2},
            'snow': {'color': (255, 250, 250), 'walkable': True, 'movement_cost': 1.3}
        }
        
        # Generate world
        self.terrain_map = self._generate_terrain()
        self.structures = self._generate_structures()
        self.items = self._generate_items()
    
    def _generate_terrain(self) -> List[List[str]]:
        """Generate terrain using noise"""
        terrain = []
        
        for y in range(self.world_height // self.tile_size):
            row = []
            for x in range(self.world_width // self.tile_size):
                # Generate noise values
                nx = x / (self.world_width // self.tile_size) * 4
                ny = y / (self.world_height // self.tile_size) * 4
                
                # Height map
                height = noise.pnoise2(nx, ny, octaves=4, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.seed)
                
                # Moisture map
                moisture = noise.pnoise2(nx + 1000, ny + 1000, octaves=4, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.seed + 1)
                
                # Temperature map
                temperature = noise.pnoise2(nx + 2000, ny + 2000, octaves=4, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=self.seed + 2)
                
                # Determine terrain type based on height, moisture, and temperature
                terrain_type = self._get_terrain_type(height, moisture, temperature)
                row.append(terrain_type)
            
            terrain.append(row)
        
        return terrain
    
    def _get_terrain_type(self, height: float, moisture: float, temperature: float) -> str:
        """Determine terrain type based on noise values"""
        # Normalize values to 0-1
        height = (height + 1) / 2
        moisture = (moisture + 1) / 2
        temperature = (temperature + 1) / 2
        
        # Determine biome
        if height < 0.3:
            return 'water'
        elif height < 0.4:
            if moisture > 0.6:
                return 'grass'
            else:
                return 'desert'
        elif height < 0.7:
            if moisture > 0.7:
                return 'forest'
            elif moisture > 0.4:
                return 'grass'
            else:
                return 'desert'
        elif height < 0.85:
            if temperature < 0.3:
                return 'snow'
            else:
                return 'mountain'
        else:
            return 'mountain'
    
    def _generate_structures(self) -> List[Dict[str, Any]]:
        """Generate structures in the world"""
        structures = []
        
        # Generate some random structures
        num_structures = random.randint(5, 15)
        
        for _ in range(num_structures):
            x = random.randint(0, (self.world_width // self.tile_size) - 1)
            y = random.randint(0, (self.world_height // self.tile_size) - 1)
            
            # Check if location is walkable
            if self.terrain_map[y][x] in ['grass', 'forest']:
                structure_type = random.choice(['ruins', 'tower', 'cave'])
                structures.append({
                    'x': x * self.tile_size,
                    'y': y * self.tile_size,
                    'type': structure_type,
                    'width': random.randint(2, 5) * self.tile_size,
                    'height': random.randint(2, 5) * self.tile_size
                })
        
        return structures
    
    def _generate_items(self) -> List[Dict[str, Any]]:
        """Generate items scattered in the world"""
        items = []
        
        # Generate items near structures
        for structure in self.structures:
            num_items = random.randint(1, 3)
            for _ in range(num_items):
                x = structure['x'] + random.randint(-50, 50)
                y = structure['y'] + random.randint(-50, 50)
                
                # Create random item
                item = ItemFactory.create_random_item(random.randint(1, 5))
                items.append({
                    'x': x,
                    'y': y,
                    'item': item
                })
        
        # Generate some random items in the world
        num_random_items = random.randint(10, 25)
        for _ in range(num_random_items):
            x = random.randint(0, self.world_width - self.tile_size)
            y = random.randint(0, self.world_height - self.tile_size)
            
            # Check if location is walkable
            tile_x = x // self.tile_size
            tile_y = y // self.tile_size
            
            if (0 <= tile_y < len(self.terrain_map) and 
                0 <= tile_x < len(self.terrain_map[0]) and
                self.terrain_map[tile_y][tile_x] in ['grass', 'forest']):
                
                item = ItemFactory.create_random_item(random.randint(1, 3))
                items.append({
                    'x': x,
                    'y': y,
                    'item': item
                })
        
        return items
    
    def get_terrain_at(self, x: float, y: float) -> str:
        """Get terrain type at specific coordinates"""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        if (0 <= tile_y < len(self.terrain_map) and 
            0 <= tile_x < len(self.terrain_map[0])):
            return self.terrain_map[tile_y][tile_x]
        
        return 'grass'  # Default
    
    def is_walkable_at(self, x: float, y: float) -> bool:
        """Check if position is walkable"""
        terrain_type = self.get_terrain_at(x, y)
        return self.terrain_types[terrain_type]['walkable']
    
    def get_movement_cost_at(self, x: float, y: float) -> float:
        """Get movement cost at position"""
        terrain_type = self.get_terrain_at(x, y)
        return self.terrain_types[terrain_type]['movement_cost']
    
    def get_terrain_color(self, terrain_type: str) -> Tuple[int, int, int]:
        """Get color for terrain type"""
        return self.terrain_types[terrain_type]['color']
    
    def render_world(self, screen: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render the world"""
        # Debug output
        print(f"Rendering world - Camera offset: ({camera_offset[0]:.0f}, {camera_offset[1]:.0f})")
        
        # Calculate visible area
        screen_width = self.settings.SCREEN_WIDTH
        screen_height = self.settings.SCREEN_HEIGHT
        
        start_x = max(0, int(camera_offset[0] // self.tile_size))
        end_x = min(len(self.terrain_map[0]), int((camera_offset[0] + screen_width) // self.tile_size) + 1)
        start_y = max(0, int(camera_offset[1] // self.tile_size))
        end_y = min(len(self.terrain_map), int((camera_offset[1] + screen_height) // self.tile_size) + 1)
        
        print(f"Visible area: ({start_x}, {start_y}) to ({end_x}, {end_y})")
        
        # Render terrain
        tiles_rendered = 0
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                terrain_type = self.terrain_map[y][x]
                color = self.get_terrain_color(terrain_type)
                
                # Calculate screen position
                screen_x = x * self.tile_size - camera_offset[0]
                screen_y = y * self.tile_size - camera_offset[1]
                
                # Draw tile
                pygame.draw.rect(screen, color, 
                               (screen_x, screen_y, self.tile_size, self.tile_size))
                
                # Draw tile border
                pygame.draw.rect(screen, (0, 0, 0), 
                               (screen_x, screen_y, self.tile_size, self.tile_size), 1)
                tiles_rendered += 1
        
        print(f"Rendered {tiles_rendered} tiles")
        
        # Render structures
        for structure in self.structures:
            screen_x = structure['x'] - camera_offset[0]
            screen_y = structure['y'] - camera_offset[1]
            
            # Only render if visible
            if (-structure['width'] <= screen_x <= screen_width and 
                -structure['height'] <= screen_y <= screen_height):
                
                # Draw structure
                color = (139, 69, 19) if structure['type'] == 'ruins' else (105, 105, 105)
                pygame.draw.rect(screen, color, 
                               (screen_x, screen_y, structure['width'], structure['height']))
                
                # Draw structure border
                pygame.draw.rect(screen, (0, 0, 0), 
                               (screen_x, screen_y, structure['width'], structure['height']), 2)
        
        # Render items
        for item_data in self.items:
            screen_x = item_data['x'] - camera_offset[0]
            screen_y = item_data['y'] - camera_offset[1]
            
            # Only render if visible
            if (-16 <= screen_x <= screen_width and -16 <= screen_y <= screen_height):
                screen.blit(item_data['item'].sprite, (screen_x, screen_y))
