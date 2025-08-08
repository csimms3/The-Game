"""
Inventory system
"""

import pygame
from typing import List, Tuple, Optional
from game.core.settings import Settings
from game.items.item import Item

class InventoryUI:
    """Inventory user interface"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        
        # Colors
        self.colors = {
            'background': (0, 0, 0, 200),
            'border': (100, 100, 100),
            'slot_bg': (50, 50, 50),
            'slot_selected': (100, 100, 100),
            'text': (255, 255, 255),
            'text_dim': (200, 200, 200),
            'equipment_slot': (80, 80, 120),
            'equipment_filled': (120, 120, 160)
        }
        
        # Inventory state
        self.is_open = False
        self.selected_slot = None
        self.dragged_item = None
        self.drag_offset = (0, 0)
        
        # Layout
        self.slot_size = 50
        self.slots_per_row = 8
        self.panel_width = 600
        self.panel_height = 400
    
    def toggle(self):
        """Toggle inventory visibility"""
        self.is_open = not self.is_open
        if not self.is_open:
            self.selected_slot = None
            self.dragged_item = None
    
    def handle_event(self, event: pygame.event.Event, player) -> bool:
        """Handle inventory events"""
        if not self.is_open:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                self.toggle()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_mouse_click(event.pos, player)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                return self._handle_mouse_release(event.pos, player)
        
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event.pos)
        
        return False
    
    def _handle_mouse_click(self, pos: Tuple[int, int], player) -> bool:
        """Handle mouse click in inventory"""
        # Check if click is in inventory area
        panel_x = (self.settings.SCREEN_WIDTH - self.panel_width) // 2
        panel_y = (self.settings.SCREEN_HEIGHT - self.panel_height) // 2
        
        if not (panel_x <= pos[0] <= panel_x + self.panel_width and 
                panel_y <= pos[1] <= panel_y + self.panel_height):
            return False
        
        # Check inventory slots
        slot = self._get_slot_at_position(pos, player)
        if slot is not None:
            if slot < len(player.inventory):
                self.dragged_item = player.inventory[slot]
                self.selected_slot = slot
                # Calculate drag offset
                slot_x, slot_y = self._get_slot_position(slot, player)
                self.drag_offset = (pos[0] - slot_x, pos[1] - slot_y)
                return True
        
        # Check equipment slots
        equip_slot = self._get_equipment_slot_at_position(pos)
        if equip_slot is not None:
            if equip_slot == 'weapon' and player.equipped_weapon:
                self.dragged_item = player.equipped_weapon
                self.selected_slot = 'weapon'
                return True
            elif equip_slot == 'armor' and player.equipped_armor:
                self.dragged_item = player.equipped_armor
                self.selected_slot = 'armor'
                return True
        
        return False
    
    def _handle_mouse_release(self, pos: Tuple[int, int], player) -> bool:
        """Handle mouse release in inventory"""
        if self.dragged_item is None:
            return False
        
        # Check if dropping on inventory slot
        slot = self._get_slot_at_position(pos, player)
        if slot is not None and slot < len(player.inventory):
            # Swap items
            if self.selected_slot == 'weapon':
                player.equipped_weapon = player.inventory[slot]
                player.inventory[slot] = self.dragged_item
            elif self.selected_slot == 'armor':
                player.equipped_armor = player.inventory[slot]
                player.inventory[slot] = self.dragged_item
            else:
                player.inventory[self.selected_slot] = player.inventory[slot]
                player.inventory[slot] = self.dragged_item
        
        # Check if dropping on equipment slot
        equip_slot = self._get_equipment_slot_at_position(pos)
        if equip_slot is not None:
            if equip_slot == 'weapon' and self.dragged_item.item_type == 'weapon':
                if self.selected_slot == 'weapon':
                    pass  # Already equipped
                else:
                    # Unequip current weapon and equip new one
                    if player.equipped_weapon:
                        player.inventory.append(player.equipped_weapon)
                    player.equipped_weapon = self.dragged_item
                    if self.selected_slot != 'weapon':
                        player.inventory.remove(self.dragged_item)
            
            elif equip_slot == 'armor' and self.dragged_item.item_type == 'armor':
                if self.selected_slot == 'armor':
                    pass  # Already equipped
                else:
                    # Unequip current armor and equip new one
                    if player.equipped_armor:
                        player.inventory.append(player.equipped_armor)
                    player.equipped_armor = self.dragged_item
                    if self.selected_slot != 'armor':
                        player.inventory.remove(self.dragged_item)
        
        self.dragged_item = None
        self.selected_slot = None
        return True
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse motion for dragging"""
        if self.dragged_item is not None:
            return True
        return False
    
    def _get_slot_at_position(self, pos: Tuple[int, int], player) -> Optional[int]:
        """Get inventory slot index at mouse position"""
        panel_x = (self.settings.SCREEN_WIDTH - self.panel_width) // 2
        panel_y = (self.settings.SCREEN_HEIGHT - self.panel_height) // 2
        
        # Inventory slots start at y + 100
        slot_y = panel_y + 100
        slot_x = panel_x + 50
        
        for i in range(len(player.inventory)):
            row = i // self.slots_per_row
            col = i % self.slots_per_row
            
            slot_rect = pygame.Rect(
                slot_x + col * (self.slot_size + 5),
                slot_y + row * (self.slot_size + 5),
                self.slot_size,
                self.slot_size
            )
            
            if slot_rect.collidepoint(pos):
                return i
        
        return None
    
    def _get_equipment_slot_at_position(self, pos: Tuple[int, int]) -> Optional[str]:
        """Get equipment slot at mouse position"""
        panel_x = (self.settings.SCREEN_WIDTH - self.panel_width) // 2
        panel_y = (self.settings.SCREEN_HEIGHT - self.panel_height) // 2
        
        # Equipment slots are at the top
        weapon_rect = pygame.Rect(panel_x + 50, panel_y + 50, self.slot_size, self.slot_size)
        armor_rect = pygame.Rect(panel_x + 120, panel_y + 50, self.slot_size, self.slot_size)
        
        if weapon_rect.collidepoint(pos):
            return 'weapon'
        elif armor_rect.collidepoint(pos):
            return 'armor'
        
        return None
    
    def _get_slot_position(self, slot: int, player) -> Tuple[int, int]:
        """Get screen position of inventory slot"""
        panel_x = (self.settings.SCREEN_WIDTH - self.panel_width) // 2
        panel_y = (self.settings.SCREEN_HEIGHT - self.panel_height) // 2
        
        slot_y = panel_y + 100
        slot_x = panel_x + 50
        
        row = slot // self.slots_per_row
        col = slot % self.slots_per_row
        
        return (
            slot_x + col * (self.slot_size + 5),
            slot_y + row * (self.slot_size + 5)
        )
    
    def render(self, screen: pygame.Surface, player):
        """Render inventory interface"""
        if not self.is_open:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Inventory panel
        panel_x = (self.settings.SCREEN_WIDTH - self.panel_width) // 2
        panel_y = (self.settings.SCREEN_HEIGHT - self.panel_height) // 2
        
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.set_alpha(230)
        panel_surface.fill(self.colors['background'])
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Border
        pygame.draw.rect(screen, self.colors['border'], 
                        (panel_x, panel_y, self.panel_width, self.panel_height), 3)
        
        # Title
        title_text = self.font_large.render("Inventory", True, self.colors['text'])
        title_rect = title_text.get_rect(center=(panel_x + self.panel_width // 2, panel_y + 25))
        screen.blit(title_text, title_rect)
        
        # Equipment slots
        self._render_equipment_slots(screen, player, panel_x, panel_y)
        
        # Inventory slots
        self._render_inventory_slots(screen, player, panel_x, panel_y)
        
        # Dragged item
        if self.dragged_item is not None:
            mouse_pos = pygame.mouse.get_pos()
            item_x = mouse_pos[0] - self.drag_offset[0]
            item_y = mouse_pos[1] - self.drag_offset[1]
            screen.blit(self.dragged_item.sprite, (item_x, item_y))
    
    def _render_equipment_slots(self, screen: pygame.Surface, player, panel_x: int, panel_y: int):
        """Render equipment slots"""
        # Weapon slot
        weapon_color = self.colors['equipment_filled'] if player.equipped_weapon else self.colors['equipment_slot']
        weapon_rect = pygame.Rect(panel_x + 50, panel_y + 50, self.slot_size, self.slot_size)
        pygame.draw.rect(screen, weapon_color, weapon_rect)
        pygame.draw.rect(screen, self.colors['border'], weapon_rect, 2)
        
        weapon_text = self.font_small.render("Weapon", True, self.colors['text'])
        screen.blit(weapon_text, (panel_x + 50, panel_y + 50 + self.slot_size + 5))
        
        if player.equipped_weapon:
            screen.blit(player.equipped_weapon.sprite, (panel_x + 55, panel_y + 55))
        
        # Armor slot
        armor_color = self.colors['equipment_filled'] if player.equipped_armor else self.colors['equipment_slot']
        armor_rect = pygame.Rect(panel_x + 120, panel_y + 50, self.slot_size, self.slot_size)
        pygame.draw.rect(screen, armor_color, armor_rect)
        pygame.draw.rect(screen, self.colors['border'], armor_rect, 2)
        
        armor_text = self.font_small.render("Armor", True, self.colors['text'])
        screen.blit(armor_text, (panel_x + 120, panel_y + 50 + self.slot_size + 5))
        
        if player.equipped_armor:
            screen.blit(player.equipped_armor.sprite, (panel_x + 125, panel_y + 55))
    
    def _render_inventory_slots(self, screen: pygame.Surface, player, panel_x: int, panel_y: int):
        """Render inventory slots"""
        slot_y = panel_y + 100
        
        for i in range(player.max_inventory_size):
            row = i // self.slots_per_row
            col = i % self.slots_per_row
            
            slot_x = panel_x + 50 + col * (self.slot_size + 5)
            slot_y_pos = slot_y + row * (self.slot_size + 5)
            
            # Slot background
            slot_color = self.colors['slot_selected'] if i == self.selected_slot else self.colors['slot_bg']
            slot_rect = pygame.Rect(slot_x, slot_y_pos, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, slot_color, slot_rect)
            pygame.draw.rect(screen, self.colors['border'], slot_rect, 1)
            
            # Item in slot
            if i < len(player.inventory):
                item = player.inventory[i]
                if item != self.dragged_item:
                    screen.blit(item.sprite, (slot_x + 2, slot_y_pos + 2))
