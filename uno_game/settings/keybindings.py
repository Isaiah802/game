"""
Module for managing game settings and keybindings.
"""
import pygame
import json
import os
 
from typing import Dict, Any

# Default keybindings
DEFAULT_KEYBINDINGS = {
    'inventory': 'i',        # Open inventory/shop
    'roll_dice': 'space',    # Roll dice
    'menu': 'escape',        # Open menu
    'fullscreen': 'f',       # Toggle fullscreen
    'confirm': 'enter',     # Confirm selection
    'back': 'backspace',     # Go back
    'up': 'up',             # Navigate up
    'down': 'down',         # Navigate down
    'left': 'left',         # Navigate left
    'right': 'right'        # Navigate right
}

# Key name mappings for display
KEY_NAMES = {
    pygame.K_a: 'A', pygame.K_b: 'B', pygame.K_c: 'C', pygame.K_d: 'D',
    pygame.K_e: 'E', pygame.K_f: 'F', pygame.K_g: 'G', pygame.K_h: 'H',
    pygame.K_i: 'I', pygame.K_j: 'J', pygame.K_k: 'K', pygame.K_l: 'L',
    pygame.K_m: 'M', pygame.K_n: 'N', pygame.K_o: 'O', pygame.K_p: 'P',
    pygame.K_q: 'Q', pygame.K_r: 'R', pygame.K_s: 'S', pygame.K_t: 'T',
    pygame.K_u: 'U', pygame.K_v: 'V', pygame.K_w: 'W', pygame.K_x: 'X',
    pygame.K_y: 'Y', pygame.K_z: 'Z', pygame.K_SPACE: 'SPACE',
    pygame.K_RETURN: 'ENTER', pygame.K_ESCAPE: 'ESC', pygame.K_BACKSPACE: 'BACKSPACE',
    pygame.K_UP: 'UP', pygame.K_DOWN: 'DOWN', pygame.K_LEFT: 'LEFT',
    pygame.K_RIGHT: 'RIGHT', pygame.K_TAB: 'TAB'
}

class Settings:
    def __init__(self, settings_file: str = 'keybindings.json'):
        """Initialize settings with a settings file path.
        
        Args:
            settings_file: Path to the settings JSON file. Defaults to 'keybindings.json'
                         in the current directory if not specified.
        """
        if not os.path.isabs(settings_file):
            # If relative path is given, make it relative to the settings module
            settings_file = os.path.join(os.path.dirname(__file__), '..', settings_file)
        
        self.settings_file = settings_file
        self.keybindings = DEFAULT_KEYBINDINGS.copy()
        self.settings = {
            'music_volume': 0.6,
            'sfx_volume': 1.0,
            'fullscreen': False
        }
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    if 'keybindings' in data:
                        # Convert string keys back to integers for pygame key constants
                        self.keybindings.update({k: int(v) for k, v in data['keybindings'].items()})
                    if 'settings' in data:
                        self.settings.update(data['settings'])
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file."""
        try:
            data = {
                'keybindings': self.keybindings,
                'settings': self.settings
            }
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_key(self, action: str) -> int:
        """Get the key for a specific action."""
        return self.keybindings.get(action, DEFAULT_KEYBINDINGS.get(action))
    
    def set_key(self, action: str, key: int):
        """Set the key for a specific action."""
        if action in DEFAULT_KEYBINDINGS:
            self.keybindings[action] = key
            self.save_settings()
    
    def reset_keybindings(self):
        """Reset all keybindings to defaults."""
        self.keybindings = DEFAULT_KEYBINDINGS.copy()
        self.save_settings()
    
    def get_key_name(self, key: int) -> str:
        """Get a display name for a key."""
        return KEY_NAMES.get(key, str(key))
    
    def get_setting(self, name: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(name, default)
    
    def set_setting(self, name: str, value: Any):
        """Set a setting value."""
        self.settings[name] = value
        self.save_settings()