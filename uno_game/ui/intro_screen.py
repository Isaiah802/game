import os
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

    def run(self, screen: pygame.Surface, audio_manager=None):
        clock = pygame.time.Clock()
        start = time.time()
        font_title = pygame.font.SysFont('Arial', 56)
        font_sub = pygame.font.SysFont('Arial', 20)

        width, height = screen.get_size()

        # play optional startup sound once at intro start and fade it near the end
        sfx_channel = None
        sound_obj = None
        fade_duration = 0.6  # seconds to fade out before the end
        if audio_manager is not None:
            try:
                # HTX.mp3 now lives in assets/sfx (moved there). Use AudioManager's sfx_folder
                sfx_path = os.path.join(audio_manager.sfx_folder, 'whoosh.mp3')
                if os.path.exists(sfx_path):
                    sound_obj = pygame.mixer.Sound(sfx_path)
                    # set initial volume according to audio manager multiplier
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

            # handle fading SFX near the end of the intro
            if sound_obj is not None and sfx_channel is not None:
                time_left = max(0.0, self.duration - (now - start))
                if time_left <= fade_duration:
                    # compute fade fraction (1 -> 0)
                    frac = max(0.0, time_left / fade_duration)
                    try:
                        sound_obj.set_volume(frac * audio_manager.get_sfx_volume())
                    except Exception:
                        pass

            if now - start >= self.duration:
                # ensure SFX is stopped
                try:
                    if sfx_channel is not None:
                        sfx_channel.stop()
                except Exception:
                    pass
                break
