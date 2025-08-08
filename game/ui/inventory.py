"""
Inventory system
"""

import pygame
from typing import List, Optional, Tuple
from game.core.settings import Settings
from game.items.item import Item

class InventoryUI:
    """Inventory user interface"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # Colors
        self.colors = {
            'background': (0, 0, 0, 200),
            'border': (100, 100, 100),
            'slot_bg': (50, 50, 50),
            'slot_selected': (100, 100, 100),
            'slot_hover': (80, 80, 80),
            'text': (255, 255, 255),
            'text_dim': (150, 150, 150),
            'equipped': (0, 255, 0),
            'rarity_common': (192, 192, 192),
            'rarity_uncommon': (0, 255, 0),
            'rarity_rare': (0, 100, 255),
            'rarity_epic': (150, 0, 255),
            'rarity_legendary': (255, 165, 0)
        }
        
        # Inventory settings
        self.slot_size = 50
        self.slots_per_row = 8
        self.max_rows = 5
        self.panel_width = self.slot_size * self.slots_per_row + 40
        self.panel_height = self.slot_size * self.max_rows + 100
        
        # State
        self.selected_slot = None
        self.dragged_item = None
        self.drag_offset = (0, 0)
        self.show_tooltip = False
        self.tooltip_item = None
        self.tooltip_pos = (0, 0)
    
    def render_inventory(self, screen: pygame.Surface, player, x: int, y: int):
        """Render the inventory interface"""
        # Background panel
        panel_rect = pygame.Rect(x, y, self.panel_width, self.panel_height)
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.set_alpha(230)
        panel_surface.fill(self.colors['background'])
        screen.blit(panel_surface, (x, y))
        
        # Border
        pygame.draw.rect(screen, self.colors['border'], panel_rect, 3)
        
        # Title
        title_text = self.font_medium.render("INVENTORY", True, self.colors['text'])
        title_rect = title_text.get_rect(center=(x + self.panel_width // 2, y + 20))
        screen.blit(title_text, title_rect)
        
        # Render inventory slots
        self._render_inventory_slots(screen, player, x + 20, y + 50)
        
        # Render equipped items
        self._render_equipped_items(screen, player, x + 20, y + self.panel_height - 80)
        
        # Render tooltip
        if self.show_tooltip and self.tooltip_item:
            self._render_tooltip(screen, self.tooltip_item, self.tooltip_pos[0], self.tooltip_pos[1])
    
    def _render_inventory_slots(self, screen: pygame.Surface, player, x: int, y: int):
        """Render inventory slots"""
        inventory = player.inventory
        max_slots = self.slots_per_row * self.max_rows
        
        for i in range(max_slots):
            slot_x = x + (i % self.slots_per_row) * (self.slot_size + 5)
            slot_y = y + (i // self.slots_per_row) * (self.slot_size + 5)
            
            # Determine slot color
            if i == self.selected_slot:
                slot_color = self.colors['slot_selected']
            else:
                slot_color = self.colors['slot_bg']
            
            # Draw slot
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, slot_color, slot_rect)
            pygame.draw.rect(screen, self.colors['border'], slot_rect, 2)
            
            # Draw item if present
            if i < len(inventory):
                item = inventory[i]
                self._render_item_in_slot(screen, item, slot_x, slot_y)
            
            # Draw slot number for empty slots
            else:
                slot_text = self.font_tiny.render(str(i + 1), True, self.colors['text_dim'])
                text_rect = slot_text.get_rect(center=slot_rect.center)
                screen.blit(slot_text, text_rect)
    
    def _render_equipped_items(self, screen: pygame.Surface, player, x: int, y: int):
        """Render equipped items section"""
        # Weapon slot
        weapon_text = self.font_small.render("Weapon:", True, self.colors['text'])
        screen.blit(weapon_text, (x, y))
        
        weapon_slot_rect = pygame.Rect(x + 80, y, self.slot_size, self.slot_size)
        pygame.draw.rect(screen, self.colors['slot_bg'], weapon_slot_rect)
        pygame.draw.rect(screen, self.colors['equipped'], weapon_slot_rect, 3)
        
        if player.equipped_weapon:
            self._render_item_in_slot(screen, player.equipped_weapon, x + 80, y)
        
        # Armor slot
        armor_text = self.font_small.render("Armor:", True, self.colors['text'])
        screen.blit(armor_text, (x + 150, y))
        
        armor_slot_rect = pygame.Rect(x + 200, y, self.slot_size, self.slot_size)
        pygame.draw.rect(screen, self.colors['slot_bg'], armor_slot_rect)
        pygame.draw.rect(screen, self.colors['equipped'], armor_slot_rect, 3)
        
        if player.equipped_armor:
            self._render_item_in_slot(screen, player.equipped_armor, x + 200, y)
    
    def _render_item_in_slot(self, screen: pygame.Surface, item: Item, x: int, y: int):
        """Render an item in a slot"""
        # Draw item sprite
        if item.sprite:
            # Scale sprite to fit slot
            scaled_sprite = pygame.transform.scale(item.sprite, (self.slot_size - 4, self.slot_size - 4))
            screen.blit(scaled_sprite, (x + 2, y + 2))
        
        # Draw rarity border
        rarity_color = self._get_rarity_color(item.rarity)
        item_rect = pygame.Rect(x + 1, y + 1, self.slot_size - 2, self.slot_size - 2)
        pygame.draw.rect(screen, rarity_color, item_rect, 2)
    
    def _get_rarity_color(self, rarity: str) -> Tuple[int, int, int]:
        """Get color for item rarity"""
        return self.colors.get(f'rarity_{rarity}', self.colors['rarity_common'])
    
    def _render_tooltip(self, screen: pygame.Surface, item: Item, x: int, y: int):
        """Render item tooltip"""
        if not item:
            return
        
        # Get item description
        description = item.get_description()
        lines = description.split('\n')
        
        # Calculate tooltip size
        max_width = 0
        line_surfaces = []
        for line in lines:
            if line.strip():
                surface = self.font_small.render(line, True, self.colors['text'])
                line_surfaces.append(surface)
                max_width = max(max_width, surface.get_width())
        
        tooltip_height = len(line_surfaces) * 20 + 10
        tooltip_width = max_width + 20
        
        # Position tooltip (avoid going off screen)
        if x + tooltip_width > self.settings.SCREEN_WIDTH:
            x = self.settings.SCREEN_WIDTH - tooltip_width - 10
        if y + tooltip_height > self.settings.SCREEN_HEIGHT:
            y = self.settings.SCREEN_HEIGHT - tooltip_height - 10
        
        # Background
        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height))
        tooltip_surface.set_alpha(230)
        tooltip_surface.fill(self.colors['background'])
        screen.blit(tooltip_surface, (x, y))
        
        # Border
        pygame.draw.rect(screen, self.colors['border'], tooltip_rect, 2)
        
        # Text
        for i, line_surface in enumerate(line_surfaces):
            screen.blit(line_surface, (x + 10, y + 5 + i * 20))
    
    def handle_mouse_event(self, event, player) -> bool:
        """Handle mouse events for inventory interaction"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_left_click(event.pos, player)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                return self._handle_left_release(event.pos, player)
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event.pos, player)
        
        return False
    
    def _handle_left_click(self, pos: Tuple[int, int], player) -> bool:
        """Handle left mouse click"""
        # Check if click is in inventory area
        # This would need to be implemented based on the inventory position
        return False
    
    def _handle_left_release(self, pos: Tuple[int, int], player) -> bool:
        """Handle left mouse release"""
        # Handle item dropping
        return False
    
    def _handle_mouse_motion(self, pos: Tuple[int, int], player) -> bool:
        """Handle mouse motion for tooltips"""
        # Update tooltip position and show/hide
        return False
