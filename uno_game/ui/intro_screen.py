import pygame
import time


class IntroScreen:
    """Simple intro/splash screen with fade-in and skip support.

    Usage:
        intro = IntroScreen(title='Zanzibar', subtitle='A Dice Game by I paid $1,152.60 to have this team name', duration=3.0)
        intro.run(screen)
    """

    def __init__(self, title: str = 'Game', subtitle: str = '', duration: float = 2.5):
        self.title = title
        self.subtitle = subtitle
        self.duration = duration
        self.bg_color = (20, 80, 40)
        self.title_color = (240, 240, 240)
        self.subtitle_color = (200, 200, 200)

    def run(self, screen: pygame.Surface):
        clock = pygame.time.Clock()
        start = time.time()
        font_title = pygame.font.SysFont('Arial', 56)
        font_sub = pygame.font.SysFont('Arial', 20)

        width, height = screen.get_size()

        running = True
        while running:
            now = time.time()
            t = min(1.0, (now - start) / max(0.01, self.duration))
            alpha = int(t * 255)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    # skip intro
                    running = False

            # draw background
            screen.fill(self.bg_color)

            # title surface
            title_surf = font_title.render(self.title, True, self.title_color)
            title_surf.set_alpha(alpha)
            tr = title_surf.get_rect(center=(width // 2, height // 2 - 20))
            screen.blit(title_surf, tr)

            if self.subtitle:
                sub_surf = font_sub.render(self.subtitle, True, self.subtitle_color)
                sub_surf.set_alpha(alpha)
                sr = sub_surf.get_rect(center=(width // 2, height // 2 + 30))
                screen.blit(sub_surf, sr)

            pygame.display.flip()
            clock.tick(60)

            if now - start >= self.duration:
                break
