"""Theme system for customizable visual styles."""

import json
import os
from typing import Dict, Tuple, Any


class Theme:
    """Manages visual themes for the game."""
    
    def __init__(self, name: str, colors: Dict[str, Any]):
        self.name = name
        self.colors = colors
    
    def get_color(self, key: str, default: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
        """Get a color from the theme."""
        return tuple(self.colors.get(key, default))
    
    def get_rgba(self, key: str, default: Tuple[int, int, int, int] = (255, 255, 255, 255)) -> Tuple[int, int, int, int]:
        """Get a color with alpha from the theme."""
        color = self.colors.get(key, default)
        if len(color) == 3:
            return (*color, 255)
        return tuple(color)


# Predefined themes
THEMES = {
    'default': Theme('Default (Green Felt)', {
        'background': (12, 80, 34),
        'card_base': (35, 40, 50),
        'card_base_current': (45, 55, 70),
        'card_rim': (180, 150, 60),
        'card_rim_current': (220, 185, 75),
        'text_primary': (255, 255, 255),
        'text_secondary': (230, 230, 230),
        'text_highlight': (255, 240, 120),
        'shadow': (0, 0, 0, 90),
        'overlay_bg': (25, 30, 40, 240),
        'success': (0, 255, 0),
        'warning': (255, 200, 0),
        'error': (255, 100, 100),
        'die_face': (245, 245, 246),
        'die_pip': (18, 18, 20),
        'chip_colors': [
            (180, 30, 30),   # red
            (30, 90, 30),    # green
            (40, 40, 120),   # blue
            (80, 40, 10),    # brown
            (160, 120, 40),  # gold
        ]
    }),
    
    'dark': Theme('Dark Mode', {
        'background': (15, 15, 20),
        'card_base': (25, 25, 30),
        'card_base_current': (35, 35, 45),
        'card_rim': (100, 100, 120),
        'card_rim_current': (150, 150, 180),
        'text_primary': (240, 240, 245),
        'text_secondary': (200, 200, 210),
        'text_highlight': (180, 220, 255),
        'shadow': (0, 0, 0, 120),
        'overlay_bg': (20, 20, 25, 250),
        'success': (80, 255, 120),
        'warning': (255, 220, 80),
        'error': (255, 120, 120),
        'die_face': (240, 240, 245),
        'die_pip': (20, 20, 25),
        'chip_colors': [
            (200, 50, 50),
            (50, 200, 80),
            (60, 120, 255),
            (200, 100, 50),
            (255, 200, 50),
        ]
    }),
    
    'casino': Theme('Casino Royale', {
        'background': (139, 0, 0),  # Dark red
        'card_base': (0, 0, 0),
        'card_base_current': (20, 0, 0),
        'card_rim': (255, 215, 0),  # Gold
        'card_rim_current': (255, 255, 100),
        'text_primary': (255, 255, 255),
        'text_secondary': (240, 240, 240),
        'text_highlight': (255, 215, 0),
        'shadow': (0, 0, 0, 140),
        'overlay_bg': (0, 0, 0, 240),
        'success': (0, 255, 100),
        'warning': (255, 200, 0),
        'error': (255, 50, 50),
        'die_face': (255, 255, 255),
        'die_pip': (0, 0, 0),
        'chip_colors': [
            (255, 0, 0),      # bright red
            (0, 255, 0),      # bright green
            (0, 100, 255),    # bright blue
            (0, 0, 0),        # black
            (255, 215, 0),    # gold
        ]
    }),
    
    'neon': Theme('Neon Nights', {
        'background': (10, 0, 30),  # Deep purple
        'card_base': (20, 5, 40),
        'card_base_current': (30, 10, 50),
        'card_rim': (255, 0, 255),  # Magenta
        'card_rim_current': (0, 255, 255),  # Cyan
        'text_primary': (0, 255, 255),
        'text_secondary': (255, 100, 255),
        'text_highlight': (255, 255, 0),
        'shadow': (255, 0, 255, 100),
        'overlay_bg': (10, 0, 30, 230),
        'success': (0, 255, 100),
        'warning': (255, 200, 0),
        'error': (255, 0, 100),
        'die_face': (40, 10, 60),
        'die_pip': (0, 255, 255),
        'chip_colors': [
            (255, 0, 255),    # magenta
            (0, 255, 255),    # cyan
            (255, 255, 0),    # yellow
            (255, 0, 100),    # hot pink
            (0, 255, 100),    # bright green
        ]
    }),
    
    'ocean': Theme('Ocean Blue', {
        'background': (10, 40, 80),
        'card_base': (20, 50, 90),
        'card_base_current': (30, 70, 120),
        'card_rim': (100, 200, 255),
        'card_rim_current': (150, 220, 255),
        'text_primary': (240, 250, 255),
        'text_secondary': (200, 230, 255),
        'text_highlight': (255, 255, 150),
        'shadow': (0, 0, 50, 120),
        'overlay_bg': (10, 30, 60, 240),
        'success': (100, 255, 200),
        'warning': (255, 200, 100),
        'error': (255, 100, 100),
        'die_face': (230, 245, 255),
        'die_pip': (20, 50, 90),
        'chip_colors': [
            (100, 150, 255),
            (50, 200, 255),
            (200, 100, 255),
            (0, 100, 200),
            (255, 200, 100),
        ]
    }),
    
    'forest': Theme('Forest Green', {
        'background': (20, 50, 20),
        'card_base': (30, 60, 30),
        'card_base_current': (40, 80, 40),
        'card_rim': (150, 200, 100),
        'card_rim_current': (200, 255, 150),
        'text_primary': (240, 255, 240),
        'text_secondary': (200, 240, 200),
        'text_highlight': (255, 255, 180),
        'shadow': (0, 20, 0, 110),
        'overlay_bg': (15, 40, 15, 240),
        'success': (100, 255, 100),
        'warning': (255, 220, 100),
        'error': (255, 120, 100),
        'die_face': (240, 250, 235),
        'die_pip': (20, 50, 20),
        'chip_colors': [
            (150, 80, 50),    # brown
            (100, 200, 100),  # light green
            (50, 150, 50),    # green
            (200, 180, 100),  # tan
            (255, 200, 100),  # light brown
        ]
    })
}


class ThemeManager:
    """Manages theme selection and persistence."""
    
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.current_theme_name = self.load_theme_preference()
        self.current_theme = THEMES.get(self.current_theme_name, THEMES['default'])
    
    def load_theme_preference(self) -> str:
        """Load theme preference from settings."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get('theme', 'default')
            except Exception:
                pass
        return 'default'
    
    def save_theme_preference(self):
        """Save current theme to settings."""
        settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except Exception:
                pass
        
        settings['theme'] = self.current_theme_name
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving theme: {e}")
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme."""
        if theme_name in THEMES:
            self.current_theme_name = theme_name
            self.current_theme = THEMES[theme_name]
            self.save_theme_preference()
            return True
        return False
    
    def get_theme(self) -> Theme:
        """Get the current theme."""
        return self.current_theme
    
    def list_themes(self) -> list:
        """List all available themes."""
        return [(name, theme.name) for name, theme in THEMES.items()]
    
    def get_color(self, key: str, default: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
        """Get a color from the current theme."""
        return self.current_theme.get_color(key, default)
    
    def get_rgba(self, key: str, default: Tuple[int, int, int, int] = (255, 255, 255, 255)) -> Tuple[int, int, int, int]:
        """Get a color with alpha from the current theme."""
        return self.current_theme.get_rgba(key, default)
