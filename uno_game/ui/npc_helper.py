"""
UI module for NPC helper character.
"""
import pygame

class NPCHelper:
    """Helper NPC that displays game rules and tips to the player."""
    
    def __init__(self, screen, font=None, image_path=None):
        """Initialize the NPC helper.
        
        Args:
            screen: Pygame surface to draw on.
            font: Font to use for text (defaults to Arial 22).
            image_path: Optional path to NPC character image.
        """
        self.screen = screen
        self.font = font or pygame.font.SysFont('Arial', 22)
        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.smoothscale(self.image, (80, 80))
            except Exception:
                self.image = None
        self.text = (
            "Welcome to Zanzibar!\n"
            "Rules:\n"
            "- Each player rolls 3 dice.\n"
            "- Try to get the best hand: Zanzibar (4,5,6) > Three of a kind > 1-2-3 > Points.\n"
            "- First player sets the roll limit for the round.\n"
            "- Winner gets chips from others.\n"
            "- Game ends after 5 rounds or if someone loses all chips.\n"
            "Press Space or Enter to start!"
        )
        self.visible = True

    def draw(self):
        """Draw the NPC helper box with text and image."""
        if not self.visible:
            return
        # Draw box in bottom left
        box_w, box_h = 420, 180
        x, y = 20, self.screen.get_height() - box_h - 20
        s = pygame.Surface((box_w, box_h))
        s.set_alpha(220)
        s.fill((30, 30, 60))
        self.screen.blit(s, (x, y))
        # Draw image
        if self.image:
            self.screen.blit(self.image, (x + 16, y + 16))
        # Draw text
        lines = self.text.split('\n')
        tx = x + 110
        ty = y + 20
        for line in lines:
            txt = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(txt, (tx, ty))
            ty += 28

    def handle_event(self, event):
        """Handle events for hiding the NPC helper.
        
        Args:
            event: Pygame event to process.
            
        Returns:
            True if the event dismissed the helper, False otherwise.
        """
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_1, pygame.K_RETURN):
            self.visible = False
            return True
        return False