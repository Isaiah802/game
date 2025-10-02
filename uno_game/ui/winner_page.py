import os
import pygame
import time


class WinnerScreen:
    """Simple winner screen with fade-in and skip support.

    Usage:
        winner = WinnerScreen(winner_name='Player 1', message='You conquered Zanzibar!')
        winner.run(screen)
    """

    def __init__(self, winner_name: str = 'Player', message: str = 'You win!', duration: float = 3.0):
        self.winner_name = winner_name
        self.message = message
        self.duration = duration
        self.bg_color = (40, 20, 60)
        self.title_color = (255, 215, 0)  # gold
        self.subtitle_color = (220, 220, 220)

    def run(self, screen: pygame.Surface, audio_manager=None):
        clock = pygame.time.Clock()
        start = time.time()
        font_title = pygame.font.SysFont('Arial', 56, bold=True)
        font_sub = pygame.font.SysFont('Arial', 24)

        width, height = screen.get_size()

        # optional victory sound
        sfx_channel = None
        sound_obj = None
        fade_duration = 0.6  # seconds to fade out near end
        if audio_manager is not None:
            try:
                sfx_path = os.path.join(audio_manager.sfx_folder, 'victory.mp3')
                if os.path.exists(sfx_path):
                    sound_obj = pygame.mixer.Sound(sfx_path)
                    base_vol = max(0.0, min(1.0, audio_manager.get_sfx_volume()))
                    sound_obj.set_volume(base_vol)
                    sfx_channel = sound_obj.play()
            except Exception:
                sound_obj = None
                sfx_channel = None

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
                    running = False

            screen.fill(self.bg_color)

            # Winner title
            title_surf = font_title.render(f"{self.winner_name} Wins!", True, self.title_color)
            title_surf.set_alpha(alpha)
            tr = title_surf.get_rect(center=(width // 2, height // 2 - 20))
            screen.blit(title_surf, tr)

            if self.message:
                sub_surf = font_sub.render(self.message, True, self.subtitle_color)
                sub_surf.set_alpha(alpha)
                sr = sub_surf.get_rect(center=(width // 2, height // 2 + 40))
                screen.blit(sub_surf, sr)

            pygame.display.flip()
            clock.tick(60)

            if sound_obj and sfx_channel:
                time_left = max(0.0, self.duration - (now - start))
                if time_left <= fade_duration:
                    frac = max(0.0, time_left / fade_duration)
                    try:
                        sound_obj.set_volume(frac * audio_manager.get_sfx_volume())
                    except Exception:
                        pass

            if now - start >= self.duration:
                try:
                    if sfx_channel:
                        sfx_channel.stop()
                except Exception:
                    pass
                break
