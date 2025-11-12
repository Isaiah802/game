"""
UI for displaying and managing food and drinks.
"""
import os
import pygame
from typing import Optional, List, Tuple, Callable
from items import ConsumableItem, Inventory, ItemType

class ConsumablesMenu:
    """A menu for displaying and using food and drink items."""
    
    def __init__(self, screen: pygame.Surface, inventory: Inventory):
        """Initialize the consumables menu.
        
        Args:
            screen: Pygame surface to draw the menu on.
            inventory: Player's inventory containing consumable items.
        """
        self.screen = screen
        self.inventory = inventory
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 16)
        self.selected_item: Optional[ConsumableItem] = None
        self.scroll_offset = 0
        self.max_items_shown = 4
        
        # Colors
        self.bg_color = (20, 20, 30)  # Solid background
        self.food_color = (200, 150, 50)    # Warm yellow for food
        self.drink_color = (50, 150, 200)   # Cool blue for drinks
        self.selected_color = (255, 255, 255)
        self.text_color = (220, 220, 220)
        
        # Load icons (you can add these later)
        self.food_icon = None
        self.drink_icon = None
        
    def draw_item(self, item: ConsumableItem, pos: Tuple[int, int], selected: bool = False):
        """Draw a single item in the menu."""
        x, y = pos
        width = 300
        height = 80
        
        # Draw item background
        color = self.food_color if item.item_type == ItemType.FOOD else self.drink_color
        if selected:
            pygame.draw.rect(self.screen, self.selected_color, (x-2, y-2, width+4, height+4))
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        
        # Draw item name
        name_surf = self.font.render(item.name, True, self.text_color)
        self.screen.blit(name_surf, (x + 10, y + 5))
        
        # Draw quantity
        quantity = self.inventory.get_item_quantity(item.name)
        quantity_surf = self.font.render(f"x{quantity}", True, self.text_color)
        self.screen.blit(quantity_surf, (x + width - 40, y + 5))
        
        # Draw description (wrapped)
        words = item.description.split()
        line = []
        y_offset = 30
        for word in words:
            line.append(word)
            text = ' '.join(line)
            if self.small_font.size(text)[0] > width - 20:
                line.pop()
                text = ' '.join(line)
                text_surf = self.small_font.render(text, True, self.text_color)
                self.screen.blit(text_surf, (x + 10, y + y_offset))
                line = [word]
                y_offset += 20
        if line:
            text = ' '.join(line)
            text_surf = self.small_font.render(text, True, self.text_color)
            self.screen.blit(text_surf, (x + 10, y + y_offset))
    
    def draw(self, items: List[ConsumableItem]):
        """Draw the consumables menu."""
        width = 650
        height = 500
        x = (self.screen.get_width() - width) // 2
        y = (self.screen.get_height() - height) // 2
        
        # Solid background
        pygame.draw.rect(self.screen, self.bg_color, (x, y, width, height))
        pygame.draw.rect(self.screen, (100, 100, 120), (x, y, width, height), 3)  # Border
        
        # Draw title
        title_surf = self.font.render("Food & Drinks Inventory", True, self.text_color)
        self.screen.blit(title_surf, (x + (width - title_surf.get_width()) // 2, y + 15))
        
        # Instructions
        inst_surf = self.small_font.render("Arrow keys: Navigate | ENTER: Use item | ESC: Close", True, self.text_color)
        self.screen.blit(inst_surf, (x + (width - inst_surf.get_width()) // 2, y + 45))
        
        # Draw items
        item_y = y + 80
        for i, item in enumerate(items[self.scroll_offset:self.scroll_offset + self.max_items_shown]):
            self.draw_item(item, (x + 10, item_y), item == self.selected_item)
            item_y += 90
        
        # Draw scroll indicators if needed
        if self.scroll_offset > 0:
            pygame.draw.polygon(self.screen, self.text_color, 
                             [(x + width//2, y + 70), (x + width//2-10, y + 60), (x + width//2+10, y + 60)])
        if self.scroll_offset + self.max_items_shown < len(items):
            pygame.draw.polygon(self.screen, self.text_color, 
                             [(x + width//2, y + height-20), (x + width//2-10, y + height-30), (x + width//2+10, y + height-30)])
    
    def handle_event(self, event: pygame.event.Event, items: List[ConsumableItem]) -> Optional[ConsumableItem]:
        """Handle input events. Returns the item to use if one was selected."""
        if event.type == pygame.KEYDOWN:
            current_index = items.index(self.selected_item) if self.selected_item else 0
            
            if event.key == pygame.K_UP:
                current_index = max(0, current_index - 1)
                self.selected_item = items[current_index]
                if current_index < self.scroll_offset:
                    self.scroll_offset = current_index
            
            elif event.key == pygame.K_DOWN:
                current_index = min(len(items) - 1, current_index + 1)
                self.selected_item = items[current_index]
                if current_index >= self.scroll_offset + self.max_items_shown:
                    self.scroll_offset = current_index - self.max_items_shown + 1
            
            elif event.key == pygame.K_RETURN and self.selected_item:
                return self.selected_item
            
            elif event.key == pygame.K_ESCAPE:
                return None
        
        return None