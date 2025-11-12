"""
UI module for the main start menu.
"""
import pygame
from typing import Callable, Optional


class Button:
    """A clickable button UI element."""
    
    def __init__(self, rect: pygame.Rect, text: str, callback: Callable[[], None], font: pygame.font.Font, bg=(200, 200, 200), fg=(0, 0, 0)):
        """Initialize a button.
        
        Args:
            rect: Rectangle defining button position and size.
            text: Text to display on the button.
            callback: Function to call when button is clicked.
            font: Font to use for button text.
            bg: Background color (default gray).
            fg: Foreground (text) color (default black).
        """
        self.rect = rect
        self.text = text
        self.callback = callback
        self.font = font
        self.bg = bg
        self.fg = fg

    def draw(self, surface: pygame.Surface):
        """Draw the button on the given surface."""
        bg = self.bg
        if getattr(self, 'hovered', False):
            # slightly darker when hovered
            bg = tuple(max(0, c - 30) for c in self.bg)
        pygame.draw.rect(surface, bg, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        txt = self.font.render(self.text, True, self.fg)
        txt_r = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_r)

    def handle_event(self, event: pygame.event.Event):
        """Handle mouse events for button interaction."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)


class StartMenu:
    """Simple Start Menu UI using pygame.

    Usage:
        menu = StartMenu(screen)
        choice = menu.run()  # returns one of: 'play', 'settings', 'change_song', 'quit'
    """

    def __init__(self, screen: pygame.Surface, width=800, height=600):
        """Initialize the start menu.
        
        Args:
            screen: Pygame surface to draw the menu on.
            width: Menu width in pixels.
            height: Menu height in pixels.
        """
        self.screen = screen
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 28)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.result: Optional[str] = None

        # Buttons will be created in build_ui
        self.buttons = []
        self.build_ui()

    def build_ui(self):
        """Build the UI elements (buttons) for the menu."""
        btn_w, btn_h = 240, 60
        start_x = (self.width - btn_w) // 2
        start_y = 220
        gap = 20

        def make_btn(i, text, key):
            """Create a button at the given index with text and result key."""
            r = pygame.Rect(start_x, start_y + i * (btn_h + gap), btn_w, btn_h)

            def cb():
                """Button click callback."""
                self.result = key

            return Button(rect=r, text=text, callback=cb, font=self.font, bg=(240, 240, 240))

        self.buttons = [
            make_btn(0, "Play", 'play'),
            make_btn(1, "Audio Settings", 'settings'),
            make_btn(2, "Change Song", 'change_song'),
            make_btn(3, "Keybindings", 'keybindings'),
            make_btn(4, "Quit", 'quit'),
        ]
        # keyboard selection index
        self.selected = 0
        # initialize hovered state
        for i, b in enumerate(self.buttons):
            b.hovered = (i == self.selected)

    def draw(self):
        """Draw the menu and all its elements."""
        self.screen.fill((20, 120, 20))
        title = self.title_font.render("Game - Start Menu", True, (255, 255, 255))
        tr = title.get_rect(center=(self.width // 2, 120))
        self.screen.blit(title, tr)

        for b in self.buttons:
            b.draw(self.screen)

        pygame.display.flip()

    def handle_events(self):
        """Handle keyboard and mouse events for menu interaction."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.result = 'quit'
            for b in self.buttons:
                b.handle_event(event)
            # keyboard navigation
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.buttons)
                    for i, b in enumerate(self.buttons):
                        b.hovered = (i == self.selected)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.buttons)
                    for i, b in enumerate(self.buttons):
                        b.hovered = (i == self.selected)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # trigger the selected button
                    self.buttons[self.selected].callback()

    def run(self) -> str:
        """Run the menu loop until the user chooses an option; returns the choice key."""
        self.result = None
        while self.result is None:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        return self.result
