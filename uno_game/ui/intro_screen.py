import os
import threading
import math
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
        self.tip_list = [
            "Tip: Press F to toggle fullscreen",
            "Tip: Press Space to roll dice",
            "Tip: You can change music in Change Song",
            "Tip: Add at least 2 players to start",
        ]
        # optional background image path (relative to project) — set before run if desired
        self.bg_image_path = None

    def run(self, screen: pygame.Surface, audio_manager=None, load_work=None):
        """
        Runs the enhanced intro screen.

        - audio_manager: optional AudioManager instance for SFX/music control
        - load_work: optional callable(progress_cb) used to load assets; should call progress_cb(0.0..1.0) as it progresses.
          If provided, loading runs in a background thread and the progress bar reflects it.
        """
        clock = pygame.time.Clock()
        start = time.time()
        font_title = pygame.font.SysFont('Arial', 56)
        font_sub = pygame.font.SysFont('Arial', 20)
        font_small = pygame.font.SysFont('Arial', 16)

        width, height = screen.get_size()

        # optional background image
        bg_image = None
        if self.bg_image_path and os.path.exists(self.bg_image_path):
            try:
                bg_image = pygame.image.load(self.bg_image_path)
                bg_image = pygame.transform.smoothscale(bg_image, (width, height))
            except Exception:
                bg_image = None

        # sound setup (play once)
        sfx_channel = None
        sound_obj = None
        fade_duration = 0.6
        if audio_manager is not None:
            try:
                sfx_path = os.path.join(audio_manager.sfx_folder, 'whoosh.mp3')
                if os.path.exists(sfx_path):
                    sound_obj = pygame.mixer.Sound(sfx_path)
                    base_vol = max(0.0, min(1.0, audio_manager.get_sfx_volume()))
                    sound_obj.set_volume(base_vol)
                    sfx_channel = sound_obj.play()
            except Exception:
                sound_obj = None
                sfx_channel = None

        # loading state (shared with worker thread)
        state = {'progress': 0.0, 'done': False, 'error': None}

        def progress_cb(p):
            try:
                state['progress'] = max(0.0, min(1.0, float(p)))
            except Exception:
                state['progress'] = 0.0

        # If a load_work callable is provided, run it in a background thread
        if load_work is not None:
            def worker():
                try:
                    load_work(progress_cb)
                except Exception as e:
                    state['error'] = str(e)
                finally:
                    state['done'] = True

            t = threading.Thread(target=worker, daemon=True)
            t.start()
        else:
            # no loader: treat duration as the loading time
            def fake_loader(cb):
                steps = max(10, int(self.duration * 10))
                for i in range(steps):
                    time.sleep(max(0.01, self.duration / steps))
                    cb((i + 1) / steps)
            t = threading.Thread(target=lambda: (fake_loader(progress_cb), state.update({'done': True})), daemon=True)
            t.start()

        running = True
        tip_idx = 0
        last_tip = time.time()
        spinner_angle = 0.0

        while running:
            now = time.time()
            elapsed = now - start
            # progress fraction (prefer real loader progress when available)
            frac = state['progress']

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    # skip intro early if user wants
                    running = False

            # draw background
            if bg_image:
                screen.blit(bg_image, (0, 0))
            else:
                screen.fill(self.bg_color)

            # title
            title_surf = font_title.render(self.title, True, self.title_color)
            tr = title_surf.get_rect(center=(width // 2, int(height * 0.35)))
            screen.blit(title_surf, tr)

            # subtitle
            if self.subtitle:
                sub_surf = font_sub.render(self.subtitle, True, self.subtitle_color)
                sr = sub_surf.get_rect(center=(width // 2, tr.bottom + 24))
                screen.blit(sub_surf, sr)

            # progress bar background
            bar_w = int(width * 0.5)
            bar_h = 18
            bar_x = (width - bar_w) // 2
            bar_y = sr.bottom + 24 if self.subtitle else tr.bottom + 24
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
            pygame.draw.rect(screen, (80, 180, 80), (bar_x + 2, bar_y + 2, int((bar_w - 4) * frac), bar_h - 4), border_radius=6)

            # spinner (animated)
            spinner_center = (bar_x + bar_w + 48, bar_y + bar_h // 2)
            spinner_radius = 10
            spinner_steps = 8
            spinner_angle += 0.08
            for i in range(spinner_steps):
                a = spinner_angle + (i * (2 * math.pi / spinner_steps))
                sx = spinner_center[0] + math.cos(a) * (spinner_radius + 6)
                sy = spinner_center[1] + math.sin(a) * (spinner_radius + 6)
                fade = int(255 * ((i + 1) / spinner_steps))
                col = (fade, fade, fade)
                pygame.draw.circle(screen, col, (int(sx), int(sy)), 4)

            # tips
            if now - last_tip > 3.0:
                tip_idx = (tip_idx + 1) % len(self.tip_list)
                last_tip = now
            tip_surf = font_small.render(self.tip_list[tip_idx], True, (200, 200, 200))
            tip_r = tip_surf.get_rect(center=(width // 2, bar_y + bar_h + 22))
            screen.blit(tip_surf, tip_r)

            # percent
            pct_surf = font_small.render(f"Loading... {int(frac * 100)}%", True, (220, 220, 220))
            screen.blit(pct_surf, (bar_x, bar_y - 26))

            # error indicator
            if state.get('error'):
                err = state['error']
                es = font_small.render(f"Load error: {err}", True, (255, 120, 120))
                screen.blit(es, (bar_x, bar_y + bar_h + 40))

            pygame.display.flip()
            clock.tick(60)

            # fade SFX near the end if audio provided
            if sound_obj is not None and sfx_channel is not None:
                time_left = max(0.0, self.duration - elapsed)
                if time_left <= fade_duration:
                    frac_f = max(0.0, time_left / fade_duration)
                    try:
                        sound_obj.set_volume(frac_f * audio_manager.get_sfx_volume())
                    except Exception:
                        pass

            # break when loader is done and a minimal display time has passed
            if state['done'] and elapsed >= min(self.duration, 0.25):
                try:
                    if sfx_channel is not None:
                        sfx_channel.stop()
                except Exception:
                    pass
                break
