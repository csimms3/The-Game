"""
Spatial hash system for performance optimization
"""

import math
from typing import List, Set, Tuple, Any
from game.core.settings import Settings

class SpatialHash:
    """Spatial hash for efficient spatial queries"""
    
    def __init__(self, cell_size: int = 64):
        self.cell_size = cell_size
        self.grid = {}
    
    def _get_cell_key(self, x: float, y: float) -> Tuple[int, int]:
        """Get cell key for position"""
        cell_x = int(x // self.cell_size)
        cell_y = int(y // self.cell_size)
        return (cell_x, cell_y)
    
    def add_entity(self, entity: Any, x: float, y: float):
        """Add entity to spatial hash"""
        cell_key = self._get_cell_key(x, y)
        if cell_key not in self.grid:
            self.grid[cell_key] = set()
        self.grid[cell_key].add(entity)
    
    def remove_entity(self, entity: Any, x: float, y: float):
        """Remove entity from spatial hash"""
        cell_key = self._get_cell_key(x, y)
        if cell_key in self.grid:
            self.grid[cell_key].discard(entity)
            if not self.grid[cell_key]:
                del self.grid[cell_key]
    
    def update_entity_position(self, entity: Any, old_x: float, old_y: float, 
                             new_x: float, new_y: float):
        """Update entity position in spatial hash"""
        old_cell = self._get_cell_key(old_x, old_y)
        new_cell = self._get_cell_key(new_x, new_y)
        
        if old_cell != new_cell:
            self.remove_entity(entity, old_x, old_y)
            self.add_entity(entity, new_x, new_y)
    
    def get_entities_in_radius(self, x: float, y: float, radius: float) -> Set[Any]:
        """Get all entities within radius of position"""
        entities = set()
        
        # Calculate cell range
        min_cell_x = int((x - radius) // self.cell_size)
        max_cell_x = int((x + radius) // self.cell_size)
        min_cell_y = int((y - radius) // self.cell_size)
        max_cell_y = int((y + radius) // self.cell_size)
        
        # Check all cells in range
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                cell_key = (cell_x, cell_y)
                if cell_key in self.grid:
                    for entity in self.grid[cell_key]:
                        # Check actual distance
                        dx = entity.x - x
                        dy = entity.y - y
                        distance = math.sqrt(dx * dx + dy * dy)
                        if distance <= radius:
                            entities.add(entity)
        
        return entities
    
    def get_entities_in_rect(self, x: float, y: float, width: float, height: float) -> Set[Any]:
        """Get all entities within rectangle"""
        entities = set()
        
        # Calculate cell range
        min_cell_x = int(x // self.cell_size)
        max_cell_x = int((x + width) // self.cell_size)
        min_cell_y = int(y // self.cell_size)
        max_cell_y = int((y + height) // self.cell_size)
        
        # Check all cells in range
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                cell_key = (cell_x, cell_y)
                if cell_key in self.grid:
                    for entity in self.grid[cell_key]:
                        # Check actual rectangle intersection
                        if (entity.x >= x and entity.x <= x + width and
                            entity.y >= y and entity.y <= y + height):
                            entities.add(entity)
        
        return entities
    
    def get_visible_entities(self, camera_x: float, camera_y: float, 
                           screen_width: int, screen_height: int) -> Set[Any]:
        """Get entities visible on screen"""
        return self.get_entities_in_rect(camera_x, camera_y, screen_width, screen_height)
    
    def clear(self):
        """Clear all entities"""
        self.grid.clear()

class RenderOptimizer:
    """Optimizes rendering by managing visible entities"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.spatial_hash = SpatialHash()
        self.visible_entities = set()
        self.last_camera_pos = (0, 0)
        self.camera_moved_threshold = 50  # Recalculate if camera moved this much
    
    def add_entity(self, entity: Any):
        """Add entity to spatial hash"""
        self.spatial_hash.add_entity(entity, entity.x, entity.y)
    
    def remove_entity(self, entity: Any):
        """Remove entity from spatial hash"""
        self.spatial_hash.remove_entity(entity, entity.x, entity.y)
        self.visible_entities.discard(entity)
    
    def update_entity_position(self, entity: Any):
        """Update entity position in spatial hash"""
        # This would need to track previous position
        # For now, just remove and re-add
        self.spatial_hash.remove_entity(entity, entity.x, entity.y)
        self.spatial_hash.add_entity(entity, entity.x, entity.y)
    
    def update_visible_entities(self, camera_x: float, camera_y: float):
        """Update list of visible entities"""
        # Check if camera moved significantly
        dx = abs(camera_x - self.last_camera_pos[0])
        dy = abs(camera_y - self.last_camera_pos[1])
        
        if dx > self.camera_moved_threshold or dy > self.camera_moved_threshold:
            # Recalculate visible entities
            self.visible_entities = self.spatial_hash.get_visible_entities(
                camera_x, camera_y, 
                self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT
            )
            self.last_camera_pos = (camera_x, camera_y)
    
    def get_visible_entities(self) -> Set[Any]:
        """Get currently visible entities"""
        return self.visible_entities
    
    def get_entities_in_radius(self, x: float, y: float, radius: float) -> Set[Any]:
        """Get entities within radius"""
        return self.spatial_hash.get_entities_in_radius(x, y, radius)
    
    def clear(self):
        """Clear all entities"""
        self.spatial_hash.clear()
        self.visible_entities.clear()
