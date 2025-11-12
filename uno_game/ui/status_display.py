"""
Visual display for active status effects on players.
"""
import pygame
from items.consumables import Effect


class StatusDisplay:
    """Displays active status effects for players during the game."""
    
    # Effect icons/colors
    EFFECT_INFO = {
        Effect.ENERGY_BOOST: {
            'color': (255, 215, 0),  # Gold
            'symbol': '⚡',
            'short_name': 'Energy'
        },
        Effect.LUCK_BOOST: {
            'color': (0, 255, 127),  # Spring green
            'symbol': '🍀',
            'short_name': 'Luck'
        },
        Effect.FOCUS_BOOST: {
            'color': (100, 149, 237),  # Cornflower blue
            'symbol': '🎯',
            'short_name': 'Focus'
        },
        Effect.MOOD_BOOST: {
            'color': (255, 105, 180),  # Hot pink
            'symbol': '😊',
            'short_name': 'Mood'
        }
    }
    
    def __init__(self):
        """Initialize the status display."""
        self.font_small = pygame.font.SysFont('Arial', 16)
        self.font_tiny = pygame.font.SysFont('Arial', 12)
        
    def draw_player_effects(self, screen: pygame.Surface, player_name: str, 
                           active_effects: dict, x: int, y: int, compact: bool = False):
        """Draw active effects for a single player.
        
        Args:
            screen: Pygame surface to draw on
            player_name: Name of the player
            active_effects: Dictionary of {Effect: turns_remaining}
            x: X coordinate for top-left
            y: Y coordinate for top-left
            compact: If True, use compact display (just icons)
        """
        if not active_effects:
            return
            
        current_x = x
        current_y = y
        
        for effect, turns_left in active_effects.items():
            if effect not in self.EFFECT_INFO:
                continue
                
            info = self.EFFECT_INFO[effect]
            
            if compact:
                # Compact mode: just colored circle with symbol
                radius = 12
                pygame.draw.circle(screen, info['color'], (current_x + radius, current_y + radius), radius)
                pygame.draw.circle(screen, (0, 0, 0), (current_x + radius, current_y + radius), radius, 2)
                
                # Draw turns remaining
                turns_surf = self.font_tiny.render(str(turns_left), True, (255, 255, 255))
                turns_rect = turns_surf.get_rect(center=(current_x + radius, current_y + radius))
                screen.blit(turns_surf, turns_rect)
                
                current_x += radius * 2 + 5
            else:
                # Full mode: colored box with name and turns
                width = 80
                height = 30
                
                # Background box
                box_rect = pygame.Rect(current_x, current_y, width, height)
                pygame.draw.rect(screen, info['color'], box_rect)
                pygame.draw.rect(screen, (0, 0, 0), box_rect, 2)
                
                # Effect name
                name_surf = self.font_small.render(info['short_name'], True, (0, 0, 0))
                name_rect = name_surf.get_rect(centerx=current_x + width//2, top=current_y + 3)
                screen.blit(name_surf, name_rect)
                
                # Turns remaining
                turns_surf = self.font_tiny.render(f"{turns_left} turns", True, (0, 0, 0))
                turns_rect = turns_surf.get_rect(centerx=current_x + width//2, bottom=current_y + height - 3)
                screen.blit(turns_surf, turns_rect)
                
                current_y += height + 5
    
    def draw_all_players_effects(self, screen: pygame.Surface, game_manager, 
                                 x: int = 10, y: int = 100):
        """Draw effects for all players in a list format.
        
        Args:
            screen: Pygame surface to draw on
            game_manager: GameManager instance with player data
            x: Starting X coordinate
            y: Starting Y coordinate
        """
        current_y = y
        
        # Title
        title_surf = self.font_small.render("Active Effects:", True, (255, 255, 255))
        screen.blit(title_surf, (x, current_y))
        current_y += 25
        
        for player_name in game_manager.player_order:
            effects = game_manager.get_active_effects(player_name)
            
            if effects:
                # Player name
                name_surf = self.font_small.render(f"{player_name}:", True, (200, 200, 200))
                screen.blit(name_surf, (x + 5, current_y))
                current_y += 20
                
                # Effects
                self.draw_player_effects(screen, player_name, effects, x + 15, current_y, compact=False)
                current_y += len(effects) * 35 + 10


def draw_compact_player_status(screen: pygame.Surface, player_name: str, chips: int,
                               active_effects: dict, x: int, y: int):
    """Draw a compact status bar for a player showing chips and effects.
    
    Args:
        screen: Pygame surface to draw on
        player_name: Name of the player
        chips: Number of chips the player has
        active_effects: Dictionary of {Effect: turns_remaining}
        x: X coordinate
        y: Y coordinate
    """
    font = pygame.font.SysFont('Arial', 18, bold=True)
    
    # Background panel
    panel_width = 200
    panel_height = 40
    panel_rect = pygame.Rect(x, y, panel_width, panel_height)
    pygame.draw.rect(screen, (40, 40, 60, 200), panel_rect)
    pygame.draw.rect(screen, (100, 100, 150), panel_rect, 2)
    
    # Player name and chips
    text = f"{player_name}: {chips} chips"
    text_surf = font.render(text, True, (255, 255, 255))
    screen.blit(text_surf, (x + 5, y + 5))
    
    # Draw effects as small icons
    if active_effects:
        display = StatusDisplay()
        effects_x = x + 5
        effects_y = y + panel_height - 20
        display.draw_player_effects(screen, player_name, active_effects, 
                                    effects_x, effects_y, compact=True)
