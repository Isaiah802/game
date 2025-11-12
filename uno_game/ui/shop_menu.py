"""
UI for the food and drink shop.
"""
import pygame
from typing import Optional, List, Tuple
from items import ConsumableItem, ItemRegistry, registry
from settings import Settings

class ShopMenu:
    """A menu for buying food and drinks."""
    
    def __init__(self, screen: pygame.Surface, player_chips: int, settings: Settings):
        """Initialize the shop menu.
        
        Args:
            screen: Pygame surface to draw the menu on.
            player_chips: Number of chips the player currently has.
            settings: Game settings object.
        """
        self.screen = screen
        self.player_chips = player_chips
        self.settings = settings
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 20)
        
        # Colors
        self.bg_color = (20, 20, 30)  # Solid background
        self.text_color = (220, 220, 220)
        self.selected_color = (255, 255, 255)
        self.price_color = (255, 215, 0)  # Gold color for prices
        self.error_color = (255, 100, 100)
        self.success_color = (100, 255, 100)
        
        # State
        self.selected_item: Optional[ConsumableItem] = None
        self.scroll_offset = 0
        self.max_items_shown = 6
        self.message = ""
        self.message_color = self.text_color
        self.message_timer = 0
        
    def draw_item(self, item: ConsumableItem, pos: Tuple[int, int], selected: bool = False):
        """Draw a single shop item."""
        x, y = pos
        width = 500
        height = 60
        
        # Background
        if selected:
            pygame.draw.rect(self.screen, (40, 40, 60), (x-5, y-5, width+10, height+10))
        
        # Item name and description
        name_surf = self.font.render(item.name, True, 
                                   self.selected_color if selected else self.text_color)
        self.screen.blit(name_surf, (x + 10, y + 5))
        
        desc_surf = self.small_font.render(item.description, True, self.text_color)
        self.screen.blit(desc_surf, (x + 10, y + 35))
        
        # Price
        price_surf = self.font.render(f"{item.cost} chips", True, self.price_color)
        price_rect = price_surf.get_rect(right=x + width - 10, centery=y + height//2)
        self.screen.blit(price_surf, price_rect)
        
    def draw(self, items: List[ConsumableItem]):
        """Draw the shop menu."""
        width = 650
        height = 550
        x = (self.screen.get_width() - width) // 2
        y = (self.screen.get_height() - height) // 2
        
        # Solid background
        pygame.draw.rect(self.screen, self.bg_color, (x, y, width, height))
        pygame.draw.rect(self.screen, (100, 100, 120), (x, y, width, height), 3)  # Border
        
        # Title and chips
        title = self.font.render("Food & Drinks Shop", True, self.text_color)
        self.screen.blit(title, (x + (width - title.get_width()) // 2, y + 20))
        
        chips = self.font.render(f"Your chips: {self.player_chips}", True, self.price_color)
        self.screen.blit(chips, (x + 20, y + 60))
        
        # Instructions
        if self.selected_item:
            inst = self.small_font.render(
                f"ENTER: Buy {self.selected_item.name} ({self.selected_item.cost} chips) | ESC: Exit",
                True, self.text_color
            )
        else:
            inst = self.small_font.render(
                "Arrow keys: Navigate | ENTER: Buy | ESC: Exit",
                True, self.text_color
            )
        self.screen.blit(inst, (x + (width - inst.get_width()) // 2, y + 90))
        
        # Message (if any)
        if self.message and pygame.time.get_ticks() < self.message_timer:
            msg_surf = self.font.render(self.message, True, self.message_color)
            msg_rect = msg_surf.get_rect(centerx=x + width//2, y=y + height - 40)
            self.screen.blit(msg_surf, msg_rect)
        
        # Draw items
        y_pos = y + 130
        visible_items = items[self.scroll_offset:self.scroll_offset + self.max_items_shown]
        for item in visible_items:
            self.draw_item(item, (x + 20, y_pos), item == self.selected_item)
            y_pos += 70
        
        # Scroll indicators
        if self.scroll_offset > 0:
            pygame.draw.polygon(self.screen, self.text_color, 
                             [(x + width//2, y + 120), (x + width//2-10, y + 110), (x + width//2+10, y + 110)])
        if self.scroll_offset + self.max_items_shown < len(items):
            pygame.draw.polygon(self.screen, self.text_color,
                             [(x + width//2, y + height-40), (x + width//2-10, y + height-50), (x + width//2+10, y + height-50)])
    
    def show_message(self, message: str, is_error: bool = False):
        """Show a temporary message."""
        self.message = message
        self.message_color = self.error_color if is_error else self.success_color
        self.message_timer = pygame.time.get_ticks() + 2000  # Show for 2 seconds
    
    def handle_event(self, event: pygame.event.Event, items: List[ConsumableItem]) -> Optional[ConsumableItem]:
        """Handle input events. Returns the item to buy if one was selected."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return None
            
            current_index = items.index(self.selected_item) if self.selected_item else 0
            
            if event.key == pygame.K_UP:
                if current_index > 0:
                    current_index -= 1
                    self.selected_item = items[current_index]
                    if current_index < self.scroll_offset:
                        self.scroll_offset = current_index
            
            elif event.key == pygame.K_DOWN:
                if current_index < len(items) - 1:
                    current_index += 1
                    self.selected_item = items[current_index]
                    if current_index >= self.scroll_offset + self.max_items_shown:
                        self.scroll_offset = current_index - self.max_items_shown + 1
            
            elif event.key == pygame.K_RETURN and self.selected_item:
                if self.player_chips >= self.selected_item.cost:
                    return self.selected_item
                else:
                    self.show_message("Not enough chips!", True)
        
        return None

def run_shop(screen: pygame.Surface, player_chips: int, settings: Settings) -> Tuple[Optional[ConsumableItem], int]:
    """
    Run the shop menu.
    Returns: (purchased_item, remaining_chips) or (None, original_chips) if cancelled
    """
    shop = ShopMenu(screen, player_chips, settings)
    items = registry.get_all_items()
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, player_chips
            
            item = shop.handle_event(event, items)
            if item is None and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None, player_chips
            elif item:
                remaining_chips = player_chips - item.cost
                shop.player_chips = remaining_chips
                shop.show_message(f"Bought {item.name}!")
                player_chips = remaining_chips
        
        shop.draw(items)
        pygame.display.flip()
        clock.tick(60)
    
    return None, player_chips