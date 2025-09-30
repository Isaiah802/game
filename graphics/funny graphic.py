import pygame
import random
import math

# --- Screen Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 180  # Frames per second

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (30, 86, 49)  # A nice table green


class Die:
    """A class to manage a single die's state, movement, and drawing."""

    def __init__(self, x, y, size=70):
        self.size = size
        self.value = random.randint(1, 6)

        # Create the base image of the die (unrotated)
        self.original_image = self._create_image()
        self.image = self.original_image.copy()  # The image that will be rotated

        # Position and movement state
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = random.uniform(-3, 3)  # Horizontal velocity
        self.vy = random.uniform(-3, 3)  # Vertical velocity

        # Rotation state
        self.angle = random.uniform(0, 360)
        self.angular_velocity = random.uniform(-4, 4)

    def _create_image(self):
        """Creates the static surface for a single die face."""
        image = pygame.Surface((self.size, self.size))
        image.fill(WHITE)
        pygame.draw.rect(image, BLACK, image.get_rect(), 3)  # Outline

        pip_radius = self.size // 10

        # Pip positions (relative to the top-left of the surface)
        positions = {
            'center': (self.size * 0.5, self.size * 0.5),
            'top_left': (self.size * 0.25, self.size * 0.25),
            'top_right': (self.size * 0.75, self.size * 0.25),
            'bottom_left': (self.size * 0.25, self.size * 0.75),
            'bottom_right': (self.size * 0.75, self.size * 0.75),
            'mid_left': (self.size * 0.25, self.size * 0.5),
            'mid_right': (self.size * 0.75, self.size * 0.5)
        }

        # Determine which pips to draw based on the die's value
        pip_map = {
            1: ['center'],
            2: ['top_left', 'bottom_right'],
            3: ['top_left', 'center', 'bottom_right'],
            4: ['top_left', 'top_right', 'bottom_left', 'bottom_right'],
            5: ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'center'],
            6: ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'mid_left', 'mid_right']
        }

        for pos_key in pip_map[self.value]:
            pygame.draw.circle(image, BLACK, positions[pos_key], pip_radius)

        return image

    def update(self):
        """Update the die's position and rotation for one frame."""
        # --- Update Rotation ---
        self.angle += self.angular_velocity
        # To avoid large numbers, keep angle between 0 and 360
        if self.angle > 360: self.angle -= 360
        if self.angle < 0: self.angle += 360

        # Create a new rotated image and update its rectangle
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=old_center)

        # --- Update Position and Bounce ---
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Bounce off the walls by reversing velocity
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.vx *= -1
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.vy *= -1

    def draw(self, surface):
        """Draw the die onto the provided surface."""
        surface.blit(self.image, self.rect)


def main():
    """Main function to run the game."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Moving & Rotating Dice")
    clock = pygame.time.Clock()

    # Create a group of dice
    num_dice = 5
    dice_group = [Die(random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT - 100)) for _ in
                  range(num_dice)]

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Update ---
        for die in dice_group:
            die.update()

        # --- Draw ---
        screen.fill(GREEN)
        for die in dice_group:
            die.draw(screen)

        pygame.display.flip()

        # --- Cap the frame rate ---
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()