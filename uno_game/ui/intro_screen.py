import os
import threading
import math
import pygame
import time
import random


class IntroScreen:
    """Simple intro/splash screen with fade-in and skip support.

    Usage:
        intro = IntroScreen(title='Zanzibar Get Ready for Battle', subtitle='A Dice Game by I paid $1,152.60 to have this team name', duration=3.0)
        intro.run(screen)
    """

    def __init__(self, title: str = 'Game', subtitle: str = '', duration: float = 30.0, **kwargs):
        self.title = title
        self.subtitle = subtitle
        self.duration = duration
        
        # Casino-themed color scheme
        self.bg_color = kwargs.get('bg_color', (20, 20, 30))  # Deep blue-black
        self.gradient_top = kwargs.get('gradient_top', (20, 20, 30, 160))  # Subtle dark gradient
        self.gradient_bottom = kwargs.get('gradient_bottom', (10, 10, 15, 220))  # Deeper gradient bottom
        self.title_color = kwargs.get('title_color', (255, 215, 0))  # Gold color for title
        self.subtitle_color = kwargs.get('subtitle_color', (220, 220, 240))  # Soft white with blue tint
        self.accent_color = kwargs.get('accent_color', (200, 20, 20))  # Deep red accent
        self.progress_color = kwargs.get('progress_color', (200, 20, 20, 180))  # Semi-transparent red
        
        # Animation settings
        self.title_glow_speed = kwargs.get('title_glow_speed', 2.0)
        self.title_glow_intensity = kwargs.get('title_glow_intensity', 0.3)
        self.subtitle_fade_speed = kwargs.get('subtitle_fade_speed', 1.5)
        self.progress_glow_speed = kwargs.get('progress_glow_speed', 3.0)
        self.gradient_opacity = kwargs.get('gradient_opacity', 150)  # 0-255
        
        # Font settings
        self.title_font_name = kwargs.get('title_font_name', 'Arial')
        self.title_font_size = kwargs.get('title_font_size', 56)
        self.subtitle_font_size = kwargs.get('subtitle_font_size', 20)
        self.tip_font_size = kwargs.get('tip_font_size', 16)
        
        # Skip settings
        self.skippable = kwargs.get('skippable', False)
        self.min_display_time = kwargs.get('min_display_time', 0.25)
        self.tip_list = [
            "Tip: Press F to toggle fullscreen",
            "Tip: Press Space to roll dice",
            "Tip: You can change music in Change Song",
            "Tip: Add at least 2 players to start",
            "Tip: Press Esc to open the menu",
        ]
        # Set the casino background image
        self.bg_image_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'ui', 'casino_background.jpg')
        # Wheel customization (list of colors or None to use defaults)
        # Expect a list where index 0 is the '0' pocket color, remaining alternate
        self.wheel_colors = kwargs.get('wheel_colors', None)

        # Wheel type: 'european' (single zero) or 'american' (double zero) or 'custom'
        # Default to 'american' to match provided reference image
        self.wheel_type = kwargs.get('wheel_type', 'american')
        # Option to force-draw a procedural casino background regardless of image
        self.force_draw_casino = kwargs.get('force_draw_casino', True)
        # Allow a completely blank background (plain fill) bypassing images/procedural
        self.use_blank_background = kwargs.get('use_blank_background', False)
        # Optional: render a roulette table layout background similar to the reference
        self.use_roulette_table = kwargs.get('use_roulette_table', True)

    def run(self, screen: pygame.Surface, audio_manager=None, load_work=None):
        """
        Runs the enhanced intro screen.

        - audio_manager: optional AudioManager instance for SFX/music control
        - load_work: optional callable(progress_cb) used to load assets; should call progress_cb(0.0..1.0) as it progresses.
          If provided, loading runs in a background thread and the progress bar reflects it.
        """
        clock = pygame.time.Clock()
        start = time.time()
        # use configured font names/sizes so visuals can be tuned from constructor kwargs
        font_title = pygame.font.SysFont(self.title_font_name, self.title_font_size)
        font_sub = pygame.font.SysFont(self.title_font_name, self.subtitle_font_size)
        font_small = pygame.font.SysFont(self.title_font_name, self.tip_font_size)

        # helper: draw a procedural casino background (curtains, neon, chandeliers, felt)
        def draw_casino_background():
            # base fill
            screen.fill((18, 16, 20))

            # left/right curtains (vertical gradient deep red) - narrower now
            cur_w = max(int(width * 0.18), 120)
            for side, x in (('left', 0), ('right', width - cur_w)):
                cur_surf = pygame.Surface((cur_w, height), pygame.SRCALPHA)
                for y in range(height):
                    t = y / max(1, height)
                    r = int(120 + 80 * (1 - t))
                    g = int(10 + 10 * (1 - t))
                    b = int(10 + 10 * (1 - t))
                    pygame.draw.line(cur_surf, (r, g, b, 255), (0, y), (cur_w, y))
                # subtle folds
                for i in range(6):
                    ox = int((i / 6.0) * cur_w * 0.6)
                    try:
                        pygame.draw.arc(cur_surf, (40, 6, 6, 40), (ox, height//8, cur_w, height//1.6), 3.0, 4.0, 2)
                    except Exception:
                        pass
                screen.blit(cur_surf, (x, 0))

            # top valance
            val_h = int(height * 0.12)
            val = pygame.Surface((width, val_h), pygame.SRCALPHA)
            for y in range(val_h):
                t = y / max(1, val_h)
                pygame.draw.line(val, (40, 10, 10, 255), (0, y), (width, y))
            screen.blit(val, (0, 0))

            # marquee/backboard + neon sign centered (bigger, with bulbs and halo)
            try:
                sign_text = 'CASINO'
                neon_font = pygame.font.SysFont(self.title_font_name, max(34, int(width * 0.04)), bold=True)
                # marquee/backboard
                board_w = int(width * 0.52)
                board_h = int(height * 0.10)
                board_surf = pygame.Surface((board_w, board_h), pygame.SRCALPHA)
                pygame.draw.rect(board_surf, (22, 16, 18, 240), (0, 0, board_w, board_h), border_radius=10)
                pygame.draw.rect(board_surf, (200, 150, 60, 220), (3, 3, board_w-6, board_h-6), width=3, border_radius=8)
                # sheen
                sheen = pygame.Surface((board_w, board_h//2), pygame.SRCALPHA)
                for yy in range(sheen.get_height()):
                    a = int(50 * (1.0 - yy / max(1, sheen.get_height())))
                    pygame.draw.line(sheen, (255,255,255,a), (0,yy), (sheen.get_width(), yy))
                board_surf.blit(sheen, (0, 2), special_flags=pygame.BLEND_RGBA_ADD)
                bx = (width - board_w) // 2
                by = int(height * 0.12) - (board_h // 2)
                screen.blit(board_surf, (bx, by))

                # bulbs around board
                bulb_r = max(8, int(board_w * 0.02))
                bulb = pygame.Surface((bulb_r*2, bulb_r*2), pygame.SRCALPHA)
                pygame.draw.circle(bulb, (255,210,110,255), (bulb_r, bulb_r), bulb_r-1)
                pygame.draw.circle(bulb, (255,250,220,140), (bulb_r, bulb_r), max(2, bulb_r//3))
                halo_size = bulb_r * 6
                halo = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
                for hr in range(halo_size//2, 0, -2):
                    alpha = int(30 * (1 - hr / (halo_size//2)))
                    pygame.draw.circle(halo, (255,200,120,alpha), (halo_size//2, halo_size//2), hr)
                spacing = max(20, board_w // 16)
                bulbs = []
                for x in range(bx + 10, bx + board_w - 10, spacing):
                    bulbs.append((x, by + 8))
                    bulbs.append((x, by + board_h - 8))
                side_step = max(12, board_h // 6)
                for y in range(by + 12, by + board_h - 12, side_step):
                    bulbs.append((bx + 8, y))
                    bulbs.append((bx + board_w - 8, y))
                for (bxp, byp) in bulbs:
                    try:
                        screen.blit(halo, (bxp - halo.get_width()//2, byp - halo.get_height()//2), special_flags=pygame.BLEND_RGBA_ADD)
                    except Exception:
                        pass
                    screen.blit(bulb, (bxp - bulb_r, byp - bulb_r), special_flags=pygame.BLEND_RGBA_ADD)

                # neon text with layered glow
                for i, a in enumerate((80, 48, 28), start=1):
                    gl = neon_font.render(sign_text, True, (255, 190, 60))
                    gl.set_alpha(a)
                    rect = gl.get_rect(center=(width // 2, int(height * 0.13)))
                    screen.blit(gl, (rect.x - i, rect.y - i), special_flags=pygame.BLEND_RGBA_ADD)
                sign_surf = neon_font.render(sign_text, True, (255, 220, 80))
                rect = sign_surf.get_rect(center=(width // 2, int(height * 0.13)))
                # drop shadow for legibility
                shadow = sign_surf.copy()
                shadow.fill((0,0,0,140), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(shadow, (rect.x+2, rect.y+3))
                screen.blit(sign_surf, rect)
            except Exception:
                pass

            # chandeliers (smaller, lower-intensity radial glows)
            for cx_off in (0.18, 0.82):
                sx = max(48, int(width * 0.08))
                chill = pygame.Surface((sx, sx), pygame.SRCALPHA)
                for r in range(sx//2, 0, -6):
                    a = int(12 * (1 - (r / (sx//2))))
                    pygame.draw.circle(chill, (255, 230, 200, a), (sx//2, sx//2), r)
                px = int(width * cx_off) - sx // 2
                py = int(height * 0.05)
                screen.blit(chill, (px, py), special_flags=pygame.BLEND_RGBA_ADD)

            # roulette/green felt under the UI (tighter, centered under the bar) - trapezoid for perspective
            felt_w = int(width * 0.62)
            felt_h = int(height * 0.14)
            top_w = int(felt_w * 0.86)
            top_offset = (felt_w - top_w) // 2
            felt = pygame.Surface((felt_w, felt_h), pygame.SRCALPHA)
            pts = [(top_offset, 0), (top_offset + top_w, 0), (felt_w, felt_h), (0, felt_h)]
            # darker, richer felt base (less neon)
            pygame.draw.polygon(felt, (14, 72, 38), pts)
            # inner highlight (soft lighter top area)
            inner = pygame.Surface((felt_w, felt_h), pygame.SRCALPHA)
            inner_pts = [(int(p[0]*0.95 + felt_w*0.025), int(p[1]*0.9 + felt_h*0.05)) for p in pts]
            pygame.draw.polygon(inner, (28, 120, 60, 90), inner_pts)
            felt.blit(inner, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            # subtle inner shadow along bottom edge
            shadow_s = pygame.Surface((felt_w, felt_h), pygame.SRCALPHA)
            for yy in range(felt_h // 3):
                a = int(40 * (yy / max(1, felt_h // 3)))
                pygame.draw.line(shadow_s, (0, 0, 0, a), (0, felt_h - yy - 1), (felt_w, felt_h - yy - 1))
            felt.blit(shadow_s, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            fx = (width - felt_w) // 2
            fy = int(height * 0.46)
            # no doorway: draw only the felt table area
            screen.blit(felt, (fx, fy), special_flags=pygame.BLEND_RGBA_ADD)

            # subtle vignette to darken edges
            try:
                vig = pygame.Surface((width, height), pygame.SRCALPHA)
                for i in range(0, max(width, height)//2, 8):
                    a = int(120 * (i / (max(width, height)//2)))
                    pygame.draw.rect(vig, (0, 0, 0, min(8, a)), (-i, -i, width + i*2, height + i*2))
                screen.blit(vig, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            except Exception:
                pass

            # distant slot machine silhouettes
            for i in range(4):
                sx = int(width * 0.06)
                sy = int(height * 0.18)
                sx_x = int(width * (0.12 + i * 0.18))
                sx_y = int(height * 0.22)
                pygame.draw.rect(screen, (30, 20, 22), (sx_x, sx_y, sx, sy), border_radius=6)
                pygame.draw.circle(screen, (60, 40, 40), (sx_x + sx - 10, sx_y + 20), 6)
                pygame.draw.circle(screen, (60, 40, 40), (sx_x + 10, sx_y + sy - 20), 6)
            # end draw_casino_background

        width, height = screen.get_size()

        # optional background image
        bg_image = None
        casino_bg = False
        if self.bg_image_path and os.path.exists(self.bg_image_path):
            try:
                bg_image = pygame.image.load(self.bg_image_path)
                bg_image = pygame.transform.smoothscale(bg_image, (width, height))
                # detect if this is a casino-themed background by filename
                casino_bg = 'casino' in os.path.basename(self.bg_image_path).lower() or 'casino' in (self.bg_image_path or '').lower()
            except Exception:
                bg_image = None
                casino_bg = False

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
        skip_prompt_shown_time = None

        # roulette wheel state (physics-like)
        wheel_angle = 0.0            # current rotation of wheel (radians)
        wheel_omega = 8.0           # angular velocity (rad/s)
        wheel_damping = 1.5         # damping coefficient applied over time
        wheel_segments = 16         # number of pockets on wheel (may be overridden for accurate wheels)
        wheel_settling = False      # whether we're easing to a target
        wheel_target_angle = None
        wheel_target_index = None
        # settle timing helpers
        settle_start_time = None
        settle_duration = 0.0
        settle_start_wheel_angle = 0.0

        # ball (orbits rim in opposite direction)
        ball_angle = 0.0
        ball_speed = -10.0
        ball_damping = 0.08
        ball_orbit_offset = 6       # px outside wheel radius
        # migration state: when a target pocket is chosen the ball will
        # animate from an outer orbit into the pocket over the settle time
        ball_migrating = False
        ball_migrate_start_radius = None
        ball_migrate_start_angle = None
        wheel_result_settled = False
        # audio tick setup
        last_tick_index = None
        tick_sfx_name = None
        tick_channel_id = 7
        landing_sfx_name = None
        bounce_sfx_name = None
        if audio_manager is not None:
            # try common tick filenames
            for candidate in ('click.wav', 'click.mp3', 'tick.wav', 'tick.mp3', 'mouse-click-290204.mp3'):
                if os.path.exists(os.path.join(audio_manager.sfx_folder, candidate)):
                    tick_sfx_name = candidate
                    break
            # find landing and bounce sounds (fallback candidates)
            for candidate in ('land.wav', 'thud.wav', 'HTX.mp3', 'dice_bounce.mp3', 'dice_b.wav'):
                if landing_sfx_name is None and os.path.exists(os.path.join(audio_manager.sfx_folder, candidate)):
                    landing_sfx_name = candidate
                if bounce_sfx_name is None and os.path.exists(os.path.join(audio_manager.sfx_folder, candidate)):
                    bounce_sfx_name = candidate
                if landing_sfx_name and bounce_sfx_name:
                    break

        # ball bounce variables
        ball_bounce_amp = 0.0
        ball_bounce_phase = 0.0
        ball_bounce_decay = 0.96
        last_bounce_phase = 0.0
        last_landing_played = False

        # --- Ambient particle ambience ---
        star_particles = []
        if self.use_blank_background:
            # No ambience on blank background
            star_particles = []
        elif casino_bg:
            # warm floating glints for casino background
            star_count = 60
            for _ in range(star_count):
                star_particles.append({
                    'x': random.random() * width,
                    'y': random.random() * height,
                    'size': random.choice([2, 2, 3, 4]),
                    'speed': random.uniform(6.0, 18.0),
                    'drift': random.uniform(-8.0, 8.0),
                    'alpha': random.randint(60, 180)
                })
        else:
            star_count = 80
            for _ in range(star_count):
                star_particles.append({
                    'x': random.random() * width,
                    'y': random.random() * height,
                    'size': random.choice([1, 1, 2]),
                    'speed': random.uniform(6.0, 30.0),
                    'drift': random.uniform(-6.0, 6.0),
                    'alpha': random.randint(30, 110)
                })

        # light sweep effect (used occasionally or on progress change)
        sweep_active = False
        sweep_x = -200
        sweep_speed = width * 1.2  # px per second
        sweep_width = int(width * 0.25)
        last_sweep = time.time()
        sweep_cooldown = 6.0 + random.random() * 6.0

        # milestone particle bursts
        milestones = [0.25, 0.5, 0.75, 1.0]
        milestone_fired = {m: False for m in milestones}
        bursts = []

        last_frac = 0.0

        # Build accurate pocket list/colors for chosen wheel type
        wheel_numbers = list(range(wheel_segments))
        wheel_color_list = None
        if getattr(self, 'wheel_type', 'european') == 'european':
            # European single-zero wheel sequence (clockwise)
            euro_seq = [0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26]
            wheel_numbers = euro_seq
            wheel_segments = len(wheel_numbers)
            # canonical red numbers on a European wheel
            red_set = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
            wheel_color_list = []
            for n in wheel_numbers:
                # keep zero as green; others red if in canonical set, else black
                if n == 0:
                    wheel_color_list.append((16, 120, 24))
                elif n in red_set:
                    wheel_color_list.append((200, 20, 20))
                else:
                    wheel_color_list.append((20, 20, 20))
        elif getattr(self, 'wheel_type', 'european') == 'american':
            # American double-zero sequence (clockwise-looking sequence)
            am_seq = [0,28,9,26,30,11,7,20,32,17,5,22,34,15,3,24,36,13,1,'00',27,10,25,29,12,8,19,31,18,6,21,33,16,4,23,35,14,2]
            wheel_numbers = am_seq
            wheel_segments = len(wheel_numbers)
            # Use canonical red set (same numeric red set applies); keep 0 and '00' green
            red_set = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
            wheel_color_list = []
            for n in wheel_numbers:
                if n == 0 or n == '00':
                    wheel_color_list.append((16, 120, 24))
                else:
                    try:
                        if int(n) in red_set:
                            wheel_color_list.append((200, 20, 20))
                        else:
                            wheel_color_list.append((20, 20, 20))
                    except Exception:
                        wheel_color_list.append((20, 20, 20))

        # if user provided explicit wheel_colors, use them (extend/fallback as needed)
        if getattr(self, 'wheel_colors', None):
            provided = list(self.wheel_colors)
            # if provided list length matches numbers, use directly
            if len(provided) >= wheel_segments:
                wheel_color_list = provided[:wheel_segments]
            else:
                # fill the rest with alternating pattern
                default_alt = [(200,20,20), (20,20,20)]
                ext = []
                for i in range(wheel_segments):
                    if i < len(provided):
                        ext.append(provided[i])
                    else:
                        ext.append(default_alt[i % 2])
                wheel_color_list = ext

        # ensure wheel_color_list always set
        if wheel_color_list is None:
            wheel_color_list = [(200,20,20) if i % 2 else (20,20,20) for i in range(wheel_segments)]

        # wheel rendering cache
        base_wheel_surf = None
        base_wheel_radius = None

        while running:
            now = time.time()
            elapsed = now - start
            # progress fraction (prefer real loader progress when available)
            frac = state['progress']

            # trigger light sweep when progress jumps noticeably
            try:
                if frac - last_frac > 0.035:
                    sweep_active = True
                    sweep_x = -sweep_width
                    last_sweep = time.time()
            except Exception:
                pass

            # milestone bursts
            for m in milestones:
                if (not milestone_fired.get(m)) and frac >= m:
                    milestone_fired[m] = True
                    # spawn a burst near the progress bar area
                    bx = (bar_x + bar_w // 2) if 'bar_x' in locals() else width // 2
                    by = (bar_y + bar_h // 2) if 'bar_y' in locals() else int(height * 0.5)
                    for i in range(18):
                        ang = random.random() * math.pi * 2
                        speed = random.uniform(60, 220)
                        bursts.append({
                            'x': bx,
                            'y': by,
                            'vx': math.cos(ang) * speed,
                            'vy': math.sin(ang) * speed * 0.6 - 40,
                            'age': 0.0,
                            'life': random.uniform(0.6, 1.2),
                            'r': random.uniform(2, 5),
                            'c': (255, 220, 140)
                        })

            last_frac = frac

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                # Skip disabled: ignore key/mouse presses for skipping

            # draw background: prefer procedural casino if requested or image detected
            if self.use_blank_background:
                # Plain fill; optionally use provided bg_color (defaults to deep blue-black)
                screen.fill(self.bg_color)
            elif self.use_roulette_table:
                # Draw a roulette table layout similar to the provided image
                table_bg = (18, 90, 52)
                screen.fill(table_bg)
                # Table area
                margin = int(min(width, height) * 0.06)
                tbl_x = margin
                tbl_y = margin
                tbl_w = width - margin * 2
                tbl_h = int(height * 0.6)
                pygame.draw.rect(screen, (10, 60, 34), (tbl_x, tbl_y, tbl_w, tbl_h))
                pygame.draw.rect(screen, (220, 220, 220), (tbl_x, tbl_y, tbl_w, tbl_h), 2)
                # Grid: three rows (1-12, 13-24, 25-36) and left column for 0/00
                left_col_w = int(tbl_w * 0.09)
                cell_w = int((tbl_w - left_col_w) / 12)
                cell_h = int(tbl_h / 3)
                # Colors
                red = (200, 20, 20)
                black = (20, 20, 20)
                green = (16, 120, 24)
                label_font = pygame.font.SysFont(self.title_font_name, max(14, int(height * 0.03)))
                num_font = pygame.font.SysFont(self.title_font_name, max(12, int(height * 0.028)))
                # Left column: 0 and 00 stacked
                left_rect = pygame.Rect(tbl_x, tbl_y, left_col_w, tbl_h)
                pygame.draw.rect(screen, green, left_rect)
                pygame.draw.rect(screen, (230,230,230), left_rect, 2)
                zero_rect = pygame.Rect(tbl_x + 4, tbl_y + 4, left_col_w - 8, cell_h - 8)
                dbl_zero_rect = pygame.Rect(tbl_x + 4, tbl_y + cell_h + 4, left_col_w - 8, cell_h * 2 - 12)
                pygame.draw.rect(screen, green, zero_rect)
                pygame.draw.rect(screen, green, dbl_zero_rect)
                # labels for 0 and 00
                z_s = num_font.render("0", True, (255,255,255))
                z_r = z_s.get_rect(center=zero_rect.center)
                screen.blit(z_s, z_r)
                zz_s = num_font.render("00", True, (255,255,255))
                zz_r = zz_s.get_rect(center=dbl_zero_rect.center)
                screen.blit(zz_s, zz_r)
                # European/US red set
                red_set = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
                # Draw numeric grid 1..36
                for r in range(3):
                    for c in range(12):
                        n = r * 12 + (c + 1)
                        x = tbl_x + left_col_w + c * cell_w
                        y = tbl_y + r * cell_h
                        rect = pygame.Rect(x, y, cell_w, cell_h)
                        col = red if n in red_set else black
                        pygame.draw.rect(screen, col, rect)
                        pygame.draw.rect(screen, (230, 230, 230), rect, 2)
                        ns = num_font.render(str(n), True, (255,255,255))
                        nr = ns.get_rect(center=rect.center)
                        screen.blit(ns, nr)
                # Bottom betting labels strip
                strip_h = int(height * 0.18)
                strip_y = tbl_y + tbl_h + int(min(height * 0.04, margin))
                strip_x = tbl_x
                strip_w = tbl_w
                pygame.draw.rect(screen, (12, 80, 34), (strip_x, strip_y, strip_w, strip_h))
                pygame.draw.rect(screen, (220, 220, 220), (strip_x, strip_y, strip_w, strip_h), 2)
                labels = [
                    ("1st 12", 0.0, 0.33),
                    ("2nd 12", 0.33, 0.66),
                    ("3rd 12", 0.66, 1.0),
                ]
                # top row of labels
                top_lab_h = int(strip_h * 0.5)
                for text, a0, a1 in labels:
                    lx = strip_x + int(strip_w * a0)
                    lw = int(strip_w * (a1 - a0))
                    lr = pygame.Rect(lx, strip_y, lw, top_lab_h)
                    pygame.draw.rect(screen, (12, 80, 34), lr)
                    pygame.draw.rect(screen, (220, 220, 220), lr, 2)
                    ts = label_font.render(text, True, (255,255,255))
                    tr = ts.get_rect(center=lr.center)
                    screen.blit(ts, tr)
                # bottom row: 1 to 18 | Even | Red | Black | Odd | 19 to 36
                bottom_items = ["1 to 18", "Even", "Red", "Black", "Odd", "19 to 36"]
                bi_w = int(strip_w / len(bottom_items))
                for i, text in enumerate(bottom_items):
                    lr = pygame.Rect(strip_x + i * bi_w, strip_y + top_lab_h, bi_w, strip_h - top_lab_h)
                    base = (12, 80, 34)
                    fill = base
                    if text == "Red":
                        fill = red
                    elif text == "Black":
                        fill = black
                    pygame.draw.rect(screen, fill, lr)
                    pygame.draw.rect(screen, (220, 220, 220), lr, 2)
                    ts = label_font.render(text, True, (255,255,255))
                    tr = ts.get_rect(center=lr.center)
                    screen.blit(ts, tr)
            elif self.force_draw_casino or casino_bg:
                # draw full procedural casino background behind UI
                try:
                    draw_casino_background()
                except Exception:
                    # fallback to image/gradient if drawing fails
                    if bg_image:
                        screen.blit(bg_image, (0, 0))
                    else:
                        screen.fill(self.bg_color)
                
            elif bg_image:
                # Draw semi-transparent gradient over the background image
                screen.blit(bg_image, (0, 0))
                gradient_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                for y in range(height):
                    progress = y / height
                    color = [
                        int(self.gradient_top[i] * (1 - progress) + self.gradient_bottom[i] * progress)
                        for i in range(3)
                    ] + [150]  # Semi-transparent overlay
                    pygame.draw.line(gradient_surf, color, (0, y), (width, y))
                screen.blit(gradient_surf, (0, 0))
            else:
                screen.fill(self.bg_color)
                # Draw a subtle gradient
                for y in range(height):
                    progress = y / height
                    color = [
                        int(self.gradient_top[i] * (1 - progress) + self.gradient_bottom[i] * progress)
                        for i in range(3)
                    ]
                    pygame.draw.line(screen, color, (0, y), (width, y))

            # --- draw ambient starfield / particles over the background but under UI ---
            # Cheap particle update (fixed small dt for stability)
            dt = 1.0 / 60.0
            for p in star_particles:
                p['y'] += p['speed'] * dt
                p['x'] += p['drift'] * dt
                if p['y'] > height + 4:
                    p['y'] = -4
                    p['x'] = random.random() * width
                    p['speed'] = random.uniform(6.0, 30.0)
                    p['drift'] = random.uniform(-6.0, 6.0)

            # draw them (small soft dots)
            for p in star_particles:
                if casino_bg:
                    # warm casino glints
                    # skip glints over the central felt area for clarity
                    felt_w_chk = int(width * 0.62)
                    felt_h_chk = int(height * 0.14)
                    felt_x = (width - felt_w_chk) // 2
                    felt_y = int(height * 0.46)
                    if felt_x - 8 <= p['x'] <= felt_x + felt_w_chk + 8 and felt_y - 8 <= p['y'] <= felt_y + felt_h_chk + 8:
                        continue
                    col = (255, 210, 120, p['alpha'])
                    s = max(2, int(p['size']))
                    surf = pygame.Surface((s * 4, s * 4), pygame.SRCALPHA)
                    for r in range(s, 0, -1):
                        a = int(p['alpha'] * (r / s) * 0.9)
                        pygame.draw.circle(surf, (col[0], col[1], col[2], a), (s * 2 - 1, s * 2 - 1), r)
                    screen.blit(surf, (int(p['x'] - s * 2 + 1), int(p['y'] - s * 2 + 1)), special_flags=pygame.BLEND_RGBA_ADD)
                else:
                    col = (200, 200, 230, p['alpha'])
                    # small glow: draw a tiny circle with alpha
                    s = max(1, int(p['size']))
                    surf = pygame.Surface((s * 3, s * 3), pygame.SRCALPHA)
                    pygame.draw.circle(surf, col, (s, s), s)
                    screen.blit(surf, (int(p['x'] - s), int(p['y'] - s)), special_flags=pygame.BLEND_PREMULTIPLIED)

            # occasionally trigger a light sweep
            now_t = time.time()
            if (not sweep_active) and (now_t - last_sweep > sweep_cooldown):
                sweep_active = True
                sweep_x = -sweep_width
                last_sweep = now_t
                sweep_cooldown = 6.0 + random.random() * 6.0

            # update and draw sweep (a soft additive glow moving across title area)
            if sweep_active:
                sweep_x += sweep_speed * dt
                # draw a large soft circle to simulate sweep
                sweep_rad = int(sweep_width * 1.5)
                sweep_s = pygame.Surface((sweep_rad * 2, sweep_rad * 2), pygame.SRCALPHA)
                for r in range(sweep_rad, 0, -6):
                    a = int(12 * (1 - (r / sweep_rad)))
                    pygame.draw.circle(sweep_s, (255, 255, 255, a), (sweep_rad, sweep_rad), r)
                # position the sweep centered vertically near title
                sweep_y = int(height * 0.32)
                screen.blit(sweep_s, (int(sweep_x - sweep_rad), sweep_y - sweep_rad), special_flags=pygame.BLEND_RGBA_ADD)
                if sweep_x - sweep_rad > width:
                    sweep_active = False

            # update bursts (milestone effects) and draw them
            for b in list(bursts):
                b['age'] += dt
                if b['age'] >= b['life']:
                    bursts.remove(b)
                    continue
                # physics
                b['vx'] *= 0.995
                b['vy'] += 20 * dt
                b['x'] += b['vx'] * dt
                b['y'] += b['vy'] * dt
                life_t = 1.0 - (b['age'] / b['life'])
                alpha = int(200 * life_t)
                r = max(1, int(b['r'] * life_t))
                surfb = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
                col = (b['c'][0], b['c'][1], b['c'][2], alpha)
                pygame.draw.circle(surfb, col, (r, r), r)
                screen.blit(surfb, (int(b['x'] - r), int(b['y'] - r)), special_flags=pygame.BLEND_RGBA_ADD)

            # Animated title glow effect
            glow = abs(math.sin(time.time() * 2)) * 0.3 + 0.7
            title_color = [int(c * glow) for c in self.title_color]
            title_surf = font_title.render(self.title, True, title_color)
            tr = title_surf.get_rect(center=(width // 2, int(height * 0.35)))
            
            # Add shadow to title
            shadow_surf = font_title.render(self.title, True, (0, 0, 0))
            shadow_rect = shadow_surf.get_rect(center=(tr.centerx + 2, tr.centery + 2))
            screen.blit(shadow_surf, shadow_rect)
            screen.blit(title_surf, tr)

            # subtitle with fade effect
            if self.subtitle:
                sub_alpha = int(255 * (abs(math.sin(time.time() * 1.5)) * 0.2 + 0.8))
                sub_surf = font_sub.render(self.subtitle, True, self.subtitle_color)
                sub_surf.set_alpha(sub_alpha)
                sr = sub_surf.get_rect(center=(width // 2, tr.bottom + 24))
                screen.blit(sub_surf, sr)

            # Modern progress bar with 3D/beveled look
            bar_w = int(width * 0.5)
            bar_h = 20
            bar_x = (width - bar_w) // 2
            bar_y = sr.bottom + 24 if self.subtitle else tr.bottom + 24

            # add a soft shadow under the bar to create depth
            try:
                sh = pygame.Surface((bar_w + 16, bar_h + 14), pygame.SRCALPHA)
                for i in range(6, 0, -1):
                    a = int(22 * (i / 6.0))
                    pygame.draw.rect(sh, (0, 0, 0, a), (8 - i, 6 - i, bar_w + (i * 0), bar_h + (i * 0)), border_radius=12)
                screen.blit(sh, (bar_x - 8, bar_y - 4), special_flags=pygame.BLEND_RGBA_SUB)
            except Exception:
                pass

            # Base background (slightly inset to give border)
            base_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
            pygame.draw.rect(screen, (36, 36, 40), base_rect, border_radius=10)

            # Outer border (subtle) to define shape
            pygame.draw.rect(screen, (60, 60, 64), base_rect, width=2, border_radius=10)

            # Inner plate (slightly lighter) to act as the groove
            inner_rect = base_rect.inflate(-6, -6)
            pygame.draw.rect(screen, (28, 28, 32), inner_rect, border_radius=8)

            # Top highlight (thin) to suggest a bevel
            highlight_rect = pygame.Rect(inner_rect.x, inner_rect.y, inner_rect.width, max(2, inner_rect.height // 4))
            highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            highlight_surf.fill((255, 255, 255, 30))
            screen.blit(highlight_surf, (highlight_rect.x, highlight_rect.y))

            # Draw progress fill with a horizontal gradient and inner bevel
            if frac > 0:
                progress_width = int((inner_rect.width) * frac)
                progress_surf = pygame.Surface((progress_width, inner_rect.height), pygame.SRCALPHA)

                # left-to-right gradient (lighter on left, deeper color towards right)
                for x in range(progress_width):
                    t = x / max(1, progress_width - 1)
                    # base accent lerp from lighter to accent
                    light = [min(255, int(c * (1.0 + 0.25 * (1 - t)))) for c in self.accent_color]
                    dark = [max(0, int(c * (0.75 + 0.25 * t))) for c in self.accent_color]
                    col = [int(light[i] * (1 - t) + dark[i] * t) for i in range(3)]
                    pygame.draw.line(progress_surf, col, (x, 0), (x, inner_rect.height))

                # add a faint top glossy strip
                gloss_h = max(2, inner_rect.height // 4)
                gloss = pygame.Surface((progress_width, gloss_h), pygame.SRCALPHA)
                for y in range(gloss_h):
                    a = int(120 * (1 - (y / max(1, gloss_h))))  # fade out
                    gloss.fill((255, 255, 255, a), special_flags=pygame.BLEND_RGBA_ADD)
                progress_surf.blit(gloss, (0, 0))

                # add inner shadow at bottom edge
                shadow = pygame.Surface((progress_width, inner_rect.height), pygame.SRCALPHA)
                for y in range(inner_rect.height // 3):
                    a = int(80 * (y / max(1, inner_rect.height // 3)))
                    shadow.fill((0, 0, 0, a), rect=pygame.Rect(0, inner_rect.height - y - 1, progress_width, 1))
                progress_surf.blit(shadow, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

                # blit progress into the inner plate with a small inset
                screen.blit(progress_surf, (inner_rect.x, inner_rect.y))

                # bevel edges on the progress fill: light on top-left, dark on bottom-right
                if progress_width > 2:
                    pygame.draw.line(screen, (255, 255, 255, 40), (inner_rect.x + 1, inner_rect.y + 1), (inner_rect.x + progress_width - 2, inner_rect.y + 1))
                    pygame.draw.line(screen, (0, 0, 0, 80), (inner_rect.x + 1, inner_rect.y + inner_rect.height - 2), (inner_rect.x + progress_width - 2, inner_rect.y + inner_rect.height - 2))

            # Roulette wheel (physics-like)
            spinner_center = (bar_x + bar_w + 56, bar_y + bar_h // 2)
            wheel_radius = max(22, int(bar_h * 2.2))
            seg_angle = 2 * math.pi / wheel_segments

            # physics update
            # pre-settle the wheel when progress reaches the lead time before completion
            pre_settle_lead = 4.0  # seconds before the bar ends to have the wheel/ball stopped
            # estimate remaining time from elapsed (more robust than using progress history)
            now = time.time()
            elapsed = now - start
            remaining_time = max(0.0, self.duration - elapsed)
            # decide a settle duration so the wheel finishes by remaining_time == pre_settle_lead
            # i.e., we want settle to complete when remaining_time == pre_settle_lead
            target_finish_lead = pre_settle_lead
            # choose an appropriate settle duration (how long the wheel should take to stop)
            desired_settle_duration = 2.0
            # trigger settle so it finishes at remaining_time == target_finish_lead
            trigger_threshold = target_finish_lead + desired_settle_duration
            if (not wheel_settling) and (not wheel_result_settled) and (remaining_time <= trigger_threshold):
                # pick a random pocket for the ball to land on
                try:
                    target_idx = random.randrange(wheel_segments)
                except Exception:
                    target_idx = 0
                wheel_target_index = target_idx
                desired_center = -(target_idx * seg_angle + seg_angle * 0.5)
                rotations = 3
                wheel_target_angle = desired_center - rotations * 2 * math.pi
                # begin settle choreography
                wheel_settling = True
                settle_start_time = now
                settle_duration = max(0.5, desired_settle_duration)
                settle_start_wheel_angle = wheel_angle
                # prepare the ball migration so it animates from its current orbit
                try:
                    ball_migrating = True
                    ball_migrate_start_radius = wheel_radius + ball_orbit_offset
                    # record the current absolute screen angle of the ball
                    ball_migrate_start_angle = ball_angle
                except Exception:
                    ball_migrating = False

            # fallback: when loading completes, if not already settling, settle immediately to match progress
            if state.get('done') and (not wheel_settling) and (not wheel_result_settled):
                target_idx = min(int(frac * wheel_segments), wheel_segments - 1)
                wheel_target_index = target_idx
                desired_center = -(target_idx * seg_angle + seg_angle * 0.5)
                rotations = 3
                wheel_target_angle = desired_center - rotations * 2 * math.pi
                wheel_settling = True
                settle_start_time = now
                settle_duration = max(0.5, desired_settle_duration)
                settle_start_wheel_angle = wheel_angle
                # immediate migration when finishing early: start the ball moving inward
                try:
                    ball_migrating = True
                    ball_migrate_start_radius = wheel_radius + ball_orbit_offset
                    ball_migrate_start_angle = ball_angle
                except Exception:
                    ball_migrating = False

            # integrate wheel rotation
            if wheel_settling:
                # If we have an explicit settle schedule, interpolate the wheel angle over that time
                if settle_start_time is not None and settle_duration > 0.0:
                    t_set = (now - settle_start_time) / settle_duration
                    t_set_clamped = max(0.0, min(1.0, t_set))
                    # ease out
                    t_e = 1.0 - (1.0 - t_set_clamped) * (1.0 - t_set_clamped)
                    wheel_angle = settle_start_wheel_angle + (wheel_target_angle - settle_start_wheel_angle) * t_e
                    # damp omega to zero smoothly
                    wheel_omega *= 0.9
                    if t_set_clamped >= 1.0:
                        wheel_angle = wheel_target_angle
                        wheel_settling = False
                        wheel_result_settled = True
                        wheel_omega = 0.0
                        # play landing SFX once
                        if (not last_landing_played) and audio_manager is not None and landing_sfx_name is not None:
                            try:
                                audio_manager.play_sound_effect(landing_sfx_name, volume=0.9)
                            except Exception:
                                pass
                        last_landing_played = True
                else:
                    # fallback to proportional easing if no timing info
                    diff = (wheel_target_angle - wheel_angle)
                    diff = (diff + math.pi) % (2 * math.pi) - math.pi
                    step = diff * min(1.0, 6.0 * dt)
                    wheel_angle += step
                    wheel_omega *= 0.92
                    if abs(diff) < 0.02 and abs(wheel_omega) < 0.05:
                        wheel_angle = wheel_target_angle
                        wheel_settling = False
                        wheel_result_settled = True
                        wheel_omega = 0.0
                        if (not last_landing_played) and audio_manager is not None and landing_sfx_name is not None:
                            try:
                                audio_manager.play_sound_effect(landing_sfx_name, volume=0.9)
                            except Exception:
                                pass
                        last_landing_played = True
            else:
                wheel_angle += wheel_omega * dt
                # apply damping to wheel so it slows gradually
                wheel_omega *= max(0.0, 1.0 - wheel_damping * dt * 0.05)

            # detect segment crossing for tick SFX
            try:
                current_seg = int(((-wheel_angle) % (2 * math.pi)) / seg_angle)
            except Exception:
                current_seg = None
            if current_seg is not None and current_seg != last_tick_index:
                # only play ticks while wheel is visibly moving
                if abs(wheel_omega) > 0.05 or wheel_settling:
                    if audio_manager is not None and tick_sfx_name is not None:
                        try:
                            # play on a reserved channel to prevent overlap
                            audio_manager.play_sound_effect(tick_sfx_name, volume=0.6, channel_id=tick_channel_id)
                        except Exception:
                            pass
                last_tick_index = current_seg

            # Note: orbiting external ball has been removed per user request.
            # We no longer update an outside ball or its bounce oscillation. Landing SFX still plays on settle.

            # build or reuse cached base wheel surface (drawn at neutral rotation)
            if base_wheel_surf is None or base_wheel_radius != wheel_radius:
                surf_size = (wheel_radius + 12) * 2
                base_wheel_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                cx = surf_size // 2
                cy = surf_size // 2
                # draw segments onto base surface
                for i in range(wheel_segments):
                    a0 = i * seg_angle
                    a1 = a0 + seg_angle
                    try:
                        col = wheel_color_list[i]
                    except Exception:
                        if getattr(self, 'wheel_colors', None) and i < len(self.wheel_colors):
                            col = self.wheel_colors[i]
                        else:
                                col = (220, 40, 40) if (i % 2) else (20, 20, 20)
                    pts = [(cx, cy)]
                    steps = 10
                    for k in range(steps + 1):
                        aa = a0 + (a1 - a0) * (k / steps)
                        px = cx + math.cos(aa) * wheel_radius
                        py = cy + math.sin(aa) * wheel_radius * 0.94
                        pts.append((int(px), int(py)))
                    pygame.draw.polygon(base_wheel_surf, col, pts)
                    # If this pocket is red-ish, draw a slightly smaller brighter inner wedge
                    try:
                        is_red = (col[0] > col[1] + 60 and col[0] > col[2] + 60)
                    except Exception:
                        is_red = False
                    if is_red:
                        brighter = (min(255, int(col[0] * 1.15)), min(255, int(col[1] * 1.15)), min(255, int(col[2] * 1.15)))
                        inner_pts = [(cx, cy)]
                        inner_radius = int(wheel_radius * 0.86)
                        for k in range(steps + 1):
                            aa = a0 + (a1 - a0) * (k / steps)
                            px = cx + math.cos(aa) * inner_radius
                            py = cy + math.sin(aa) * inner_radius * 0.94
                            inner_pts.append((int(px), int(py)))
                        pygame.draw.polygon(base_wheel_surf, brighter, inner_pts)
                    # draw white circular pocket label and number similar to reference image
                    try:
                        label = str(wheel_numbers[i])
                    except Exception:
                        label = str(i)
                    mid_a = (a0 + a1) / 2.0
                    # place the white disc slightly inside the pocket center (a touch smaller for neatness)
                    tx = cx + math.cos(mid_a) * (wheel_radius * 0.78)
                    ty = cy + math.sin(mid_a) * (wheel_radius * 0.78) * 0.92
                    label_r = max(9, int(wheel_radius * 0.16))
                    # draw a colored outer ring so the pocket color shows around the white label
                    outer_ring_r = int(label_r + max(2, wheel_radius * 0.04))
                    try:
                        pocket_col = wheel_color_list[i]
                    except Exception:
                        pocket_col = col
                    # outer colored ring (slightly darker for contrast)
                    rim_col = tuple(max(0, min(255, int(c * 0.9))) for c in pocket_col)
                    pygame.draw.circle(base_wheel_surf, rim_col, (int(tx), int(ty)), outer_ring_r)
                    # inner white disc where number sits
                    # make the pocket label disc less visually ball-like (lower alpha, slightly smaller)
                    inner_white_r = max(6, int(label_r * 0.7))
                    try:
                        pygame.draw.circle(base_wheel_surf, (235, 235, 235, 180), (int(tx), int(ty)), inner_white_r)
                        pygame.draw.circle(base_wheel_surf, (18, 18, 20, 200), (int(tx), int(ty)), inner_white_r, width=2)
                    except Exception:
                        # fallback to opaque if RGBA draw not supported
                        pygame.draw.circle(base_wheel_surf, (235, 235, 235), (int(tx), int(ty)), inner_white_r)
                        pygame.draw.circle(base_wheel_surf, (18, 18, 20), (int(tx), int(ty)), inner_white_r, width=2)
                    # choose text color: red if pocket color is red-like, white for green pockets, else black
                    num_color = (20,20,20)
                    try:
                        pc = wheel_color_list[i]
                        if pc[0] > 180 and pc[1] < 80:  # red-ish
                            num_color = (180, 20, 20)
                        if pc[1] > pc[0] and pc[1] > pc[2]:  # green-ish
                            num_color = (255,255,255)
                    except Exception:
                        pass
                    # pocket label font scales with wheel radius for consistent look
                    label_font = pygame.font.SysFont(self.title_font_name, max(10, int(wheel_radius * 0.18)))
                    num_surf = label_font.render(label, True, num_color)
                    num_rect = num_surf.get_rect(center=(int(tx), int(ty)))
                    base_wheel_surf.blit(num_surf, num_rect)
                    # draw small metal rivet at the outer rim between pockets
                    # rivet on the rim: slightly further out and with subtle highlight
                    rivet_r = max(2, int(wheel_radius * 0.035))
                    rim_x = cx + math.cos(mid_a) * (wheel_radius + 10)
                    rim_y = cy + math.sin(mid_a) * (wheel_radius + 10) * 0.92
                    # base metal
                    pygame.draw.circle(base_wheel_surf, (140,140,140), (int(rim_x), int(rim_y)), rivet_r)
                    # small darker inner to suggest depth
                    pygame.draw.circle(base_wheel_surf, (90,90,90), (int(rim_x), int(rim_y)), max(1, rivet_r - 1))
                    # tiny highlight
                    pygame.draw.circle(base_wheel_surf, (255,255,255,150), (int(rim_x - max(1, rivet_r//2)), int(rim_y - max(1, rivet_r//2))), 1)
                base_wheel_radius = wheel_radius
                # draw rim with subtle bevel (concentric rings for 3D look)
                for r in range(wheel_radius + 8, wheel_radius - 1, -1):
                    t = (r - (wheel_radius - 1)) / (9.0)
                    light = int(40 + (80 * (1 - t)))
                    dark = int(18 + (30 * t))
                    pygame.draw.circle(base_wheel_surf, (dark, dark, dark), (cx, cy), r)
                # thin metallic outer stroke
                pygame.draw.circle(base_wheel_surf, (110, 110, 110), (cx, cy), wheel_radius + 6, width=3)
                # center hub with highlight
                pygame.draw.circle(base_wheel_surf, (36, 36, 40), (cx, cy), int(wheel_radius * 0.25))
                pygame.draw.circle(base_wheel_surf, (100, 100, 106), (cx, cy), int(wheel_radius * 0.12))
                # spokes/separators
                for i in range(wheel_segments):
                    aa = i * seg_angle
                    x1 = cx + math.cos(aa) * (wheel_radius * 0.2)
                    y1 = cy + math.sin(aa) * (wheel_radius * 0.2) * 0.94
                    x2 = cx + math.cos(aa) * (wheel_radius + 1)
                    y2 = cy + math.sin(aa) * (wheel_radius + 1) * 0.94
                    pygame.draw.line(base_wheel_surf, (10, 10, 12), (int(x1), int(y1)), (int(x2), int(y2)), 2)

            # rotate cached wheel surface by current wheel_angle (convert to degrees)
            deg = -math.degrees(wheel_angle)  # negative to match rotation direction
            rot = pygame.transform.rotozoom(base_wheel_surf, deg, 1.0)
            rw, rh = rot.get_size()
            wheel_pos = (spinner_center[0] - rw // 2, spinner_center[1] - rh // 2)
            # draw multi-layer soft shadow for wheel to ground it on the felt (3D effect)
            try:
                ws = pygame.Surface((rw + 40, rh + 40), pygame.SRCALPHA)
                # layered ellipses with decreasing alpha/size to simulate blur
                for i, a in enumerate((100, 60, 28), start=0):
                    rx = int((rw + 20) * (1.0 - i * 0.06))
                    ry = int((rh + 12) * (1.0 - i * 0.12))
                    cx_off = (ws.get_width() - rx) // 2
                    cy_off = (ws.get_height() - ry) // 2
                    pygame.draw.ellipse(ws, (0, 0, 0, a), (cx_off, cy_off, rx, ry))
                screen.blit(ws, (wheel_pos[0] - 20, wheel_pos[1] + int(rh * 0.55)), special_flags=pygame.BLEND_RGBA_SUB)
            except Exception:
                pass
            screen.blit(rot, wheel_pos)
            # slight rim specular: draw a moving highlight that follows wheel rotation
            try:
                spec = pygame.Surface((rw, rh), pygame.SRCALPHA)
                # pick a point on the rim based on wheel_angle
                highlight_angle = -wheel_angle + 0.3
                hr = int(wheel_radius * 0.6)
                hx = rw // 2 + int(math.cos(highlight_angle) * hr)
                hy = rh // 2 + int(math.sin(highlight_angle) * hr * 0.92)
                # small radial gradient for specular
                for s in range(8, 0, -1):
                    alpha = int(18 * (s / 8.0))
                    pygame.draw.circle(spec, (255, 255, 255, alpha), (hx, hy), s)
                screen.blit(spec, wheel_pos, special_flags=pygame.BLEND_RGBA_ADD)
            except Exception:
                pass
            # draw the ball: normally it orbits the rim, but when a target pocket
            # is chosen we animate the ball migrating inward into that pocket
            try:
                orbit_radius = wheel_radius + ball_orbit_offset
                ball_r = max(4, int(wheel_radius * 0.08))
                if wheel_target_index is None and (not ball_migrating):
                    # free orbiting ball (screen-space absolute angle stored in ball_angle)
                    ball_angle += ball_speed * dt
                    # small damping to slow orbital speed subtly
                    ball_speed *= max(0.0, 1.0 - ball_damping * dt)
                    bx = spinner_center[0] + math.cos(ball_angle) * orbit_radius
                    by = spinner_center[1] + math.sin(ball_angle) * orbit_radius * 0.92
                    pygame.draw.circle(screen, (10, 10, 10, 160), (int(bx)+2, int(by)+3), ball_r)
                    pygame.draw.circle(screen, (245, 245, 245), (int(bx), int(by)), ball_r)
                else:
                    # we have a target or are migrating: compute migration progress
                    mid_a = (wheel_target_index * seg_angle) + (seg_angle * 0.5) if wheel_target_index is not None else 0.0
                    # final screen angle where the ball should rest when settled
                    final_screen_angle = (mid_a + wheel_target_angle) if (wheel_target_angle is not None) else (mid_a + wheel_angle)
                    # compute normalized settle progress (if available)
                    if settle_start_time is not None and settle_duration > 0.0:
                        t_set = (now - settle_start_time) / settle_duration
                        t_clamped = max(0.0, min(1.0, t_set))
                    else:
                        t_clamped = 1.0 if wheel_result_settled else 0.0
                    # ease for a pleasing inward motion
                    t_e = 1.0 - pow(1.0 - t_clamped, 3)
                    start_r = (ball_migrate_start_radius if ball_migrate_start_radius is not None else orbit_radius)
                    end_r = max( max(8, int(wheel_radius * 0.75)), int(wheel_radius * 0.82) )
                    curr_r = start_r + (end_r - start_r) * t_e
                    start_a = (ball_migrate_start_angle if ball_migrate_start_angle is not None else ball_angle)
                    # interpolate angle from start to final (wrap properly)
                    diff = (final_screen_angle - start_a)
                    # wrap difference to [-pi, pi]
                    diff = (diff + math.pi) % (2 * math.pi) - math.pi
                    curr_a = start_a + diff * t_e
                    bx = spinner_center[0] + math.cos(curr_a) * curr_r
                    by = spinner_center[1] + math.sin(curr_a) * curr_r * 0.92
                    # small shadow and ball
                    pygame.draw.circle(screen, (10, 10, 10, 160), (int(bx)+2, int(by)+3), ball_r)
                    pygame.draw.circle(screen, (245, 245, 245), (int(bx), int(by)), ball_r)
                    # if migration completed, snap final values and trigger bounce
                    if t_clamped >= 1.0:
                        try:
                            ball_migrating = False
                            ball_angle = final_screen_angle
                            # set small bounce to imply settling
                            ball_bounce_amp = 6.0
                            ball_bounce_phase = 0.0
                            # play a landing/bounce sound if available
                            if (not last_landing_played) and audio_manager is not None and landing_sfx_name is not None:
                                try:
                                    audio_manager.play_sound_effect(landing_sfx_name, volume=0.9)
                                except Exception:
                                    pass
                        except Exception:
                            pass
                # handle bounce after landing
                if wheel_result_settled or (not ball_migrating and ball_bounce_amp > 0.01):
                    # simple decaying vertical bounce mapped to y-position
                    ball_bounce_phase += dt * 18.0
                    bounce_y = math.fabs(math.sin(ball_bounce_phase)) * ball_bounce_amp
                    # decay amplitude
                    ball_bounce_amp *= ball_bounce_decay
                    # apply bounce to last drawn ball by shifting a small amount upward
                    # (we redraw shadow/ball above, so adjust by negative bounce)
                    # to keep code simple we don't re-blit; instead a tiny highlight near the ball
                    # Optionally, if more precision is desired we could store last bx,by and re-blit.
                    pass
            except Exception:
                pass
            # draw center hub and rim onto rotated image instead (so they rotate with wheel)
            # we added hub/rim/spokes to base_wheel_surf when caching; nothing more to draw here

            # Orbiting ball removed — no outside ball is drawn.

            # tips
            if now - last_tip > 3.0:
                tip_idx = (tip_idx + 1) % len(self.tip_list)
                last_tip = now
            tip_surf = font_small.render(self.tip_list[tip_idx], True, (200, 200, 200))
            tip_r = tip_surf.get_rect(center=(width // 2, bar_y + bar_h + 22))
            screen.blit(tip_surf, tip_r)

            # Skip prompt removed

            # percent
            pct_surf = font_small.render(f"Loading... {int(frac * 100)}%", True, (220, 220, 220))
            screen.blit(pct_surf, (bar_x, bar_y - 26))

            # Enhanced error display
            if state.get('error'):
                err = state['error']
                # Create error background
                error_height = 60
                error_y = bar_y + bar_h + 30
                error_surface = pygame.Surface((width * 0.8, error_height), pygame.SRCALPHA)
                pygame.draw.rect(error_surface, (255, 0, 0, 50), error_surface.get_rect(), border_radius=10)
                
                # Error icon (X symbol)
                icon_size = 24
                icon_x = 20
                pygame.draw.line(error_surface, (255, 100, 100), 
                               (icon_x, error_height//2 - icon_size//2),
                               (icon_x + icon_size, error_height//2 + icon_size//2), 3)
                pygame.draw.line(error_surface, (255, 100, 100),
                               (icon_x, error_height//2 + icon_size//2),
                               (icon_x + icon_size, error_height//2 - icon_size//2), 3)
                
                # Error message with word wrap
                words = f"Error: {err}".split()
                lines = []
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    test_surface = font_small.render(test_line, True, (255, 120, 120))
                    if test_surface.get_width() < width * 0.7:
                        current_line.append(word)
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Render error message lines
                for i, line in enumerate(lines):
                    error_text = font_small.render(line, True, (255, 120, 120))
                    error_surface.blit(error_text, (icon_x + icon_size + 20, 10 + i * 20))
                
                # Add pulsing effect to error message
                error_alpha = int(255 * (abs(math.sin(time.time() * 2)) * 0.2 + 0.8))
                error_surface.set_alpha(error_alpha)
                
                # Display error surface
                screen.blit(error_surface, ((width - error_surface.get_width())//2, error_y))
                
                # Retry button
                retry_text = font_sub.render("Press R to retry", True, (255, 200, 200))
                retry_rect = retry_text.get_rect(center=(width//2, error_y + error_height + 20))
                screen.blit(retry_text, retry_rect)

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

            # break when loader is done and minimal display time has passed
            if state['done'] and elapsed >= min(self.duration, self.min_display_time):
                try:
                    if sfx_channel is not None:
                        sfx_channel.stop()
                except Exception:
                    pass
                break
