"""
UI for changing game keybindings.
"""
import pygame
from typing import Dict, Optional, Tuple
from settings import Settings, KEY_NAMES

class KeybindingsMenu:
    """Menu for viewing and changing game keybindings."""
    
    def __init__(self, screen: pygame.Surface, settings: Settings):
        self.screen = screen
        self.settings = settings
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 20)
        
        # Colors
        self.bg_color = (20, 20, 30)  # Solid background instead of semi-transparent
        self.text_color = (220, 220, 220)
        self.selected_color = (255, 255, 255)
        self.key_color = (100, 200, 255)
        self.action_color = (200, 200, 200)
        
        # State
        self.waiting_for_key = False
        self.scroll_offset = 0
        self.max_visible_bindings = 8
        # Initialize selected action to first keybinding
        self.selected_action = next(iter(self.settings.keybindings.keys()), None)
        
        # Simplified action descriptions (shorter)
        self.action_descriptions = {
            'inventory': 'Food & Drinks',
            'roll_dice': 'Roll Dice',
            'menu': 'Menu',
            'fullscreen': 'Fullscreen',
            'confirm': 'Confirm',
            'back': 'Cancel',
            'up': 'Up',
            'down': 'Down',
            'left': 'Left',
            'right': 'Right'
        }
    
    def draw_binding(self, action: str, key: int, pos: Tuple[int, int], selected: bool = False):
        """Draw a single keybinding."""
        x, y = pos
        width = 640
        height = 40
        
        # Background for selected item
        if selected:
            pygame.draw.rect(self.screen, (60, 80, 120), (x-5, y-5, width+10, height+10), border_radius=5)
        
        # Action name
        action_text = action.replace('_', ' ').title()
        desc = self.action_descriptions.get(action, action_text)
        action_surf = self.font.render(f"{desc}", True, 
                                     self.selected_color if selected else self.action_color)
        self.screen.blit(action_surf, (x, y + 10))
        
        # Key name (on the right)
        key_name = self.settings.get_key_name(key)
        if self.waiting_for_key and selected:
            key_name = "Press any key..."
        key_surf = self.font.render(key_name, True, 
                                  (255, 255, 100) if selected else self.key_color)
        key_rect = key_surf.get_rect(right=x + width - 10, centery=y + height//2)
        self.screen.blit(key_surf, key_rect)
    
    def draw(self):
        """Draw the keybindings menu."""
        width = 700
        height = 550
        x = (self.screen.get_width() - width) // 2
        y = (self.screen.get_height() - height) // 2
        
        # Solid background
        pygame.draw.rect(self.screen, self.bg_color, (x, y, width, height))
        pygame.draw.rect(self.screen, (100, 100, 120), (x, y, width, height), 3)  # Border
        
        # Title
        title = self.font.render("Keybindings", True, self.text_color)
        self.screen.blit(title, (x + (width - title.get_width()) // 2, y + 20))
        
        # Instructions
        if self.waiting_for_key:
            inst = self.small_font.render("Press any key to bind, ESC to cancel", True, self.text_color)
        else:
            inst = self.small_font.render("Arrow keys: Navigate | Enter: Change | R: Reset | ESC: Back", True, self.text_color)
        self.screen.blit(inst, (x + (width - inst.get_width()) // 2, y + 60))
        
        # Draw keybindings
        y_pos = y + 100
        visible_actions = list(self.settings.keybindings.items())[self.scroll_offset:
                                                                self.scroll_offset + self.max_visible_bindings]
        
        for action, key in visible_actions:
            self.draw_binding(action, key, (x + 30, y_pos), action == self.selected_action)
            y_pos += 50
        
        # Scroll indicators
        if self.scroll_offset > 0:
            pygame.draw.polygon(self.screen, self.text_color, 
                             [(x + width//2, y + 85), (x + width//2 - 10, y + 75), (x + width//2 + 10, y + 75)])
        if self.scroll_offset + self.max_visible_bindings < len(self.settings.keybindings):
            pygame.draw.polygon(self.screen, self.text_color,
                             [(x + width//2, y + height - 15), (x + width//2 - 10, y + height - 25), (x + width//2 + 10, y + height - 25)])
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events. Returns True if menu should close."""
        if self.waiting_for_key:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.waiting_for_key = False
                else:
                    self.settings.set_key(self.selected_action, event.key)
                    self.waiting_for_key = False
            return False
        
        if event.type == pygame.KEYDOWN:
            actions = list(self.settings.keybindings.keys())
            current_idx = actions.index(self.selected_action) if self.selected_action else 0
            
            if event.key == pygame.K_ESCAPE:
                return True
                
            elif event.key == pygame.K_r:
                self.settings.reset_keybindings()
                
            elif event.key == pygame.K_UP:
                if current_idx > 0:
                    current_idx -= 1
                    self.selected_action = actions[current_idx]
                    if current_idx < self.scroll_offset:
                        self.scroll_offset = current_idx
                        
            elif event.key == pygame.K_DOWN:
                if current_idx < len(actions) - 1:
                    current_idx += 1
                    self.selected_action = actions[current_idx]
                    if current_idx >= self.scroll_offset + self.max_visible_bindings:
                        self.scroll_offset = current_idx - self.max_visible_bindings + 1
                        
            elif event.key == pygame.K_RETURN and self.selected_action:
                self.waiting_for_key = True
        
        return False