"""Main pygame launcher and dice demo using AudioManager for music.

Controls (Dice Demo):
 - R: Roll dice (plays SFX if available)
 - Esc: Return to menu

Run without args to start the Start Menu. The menu exposes:
 - Play (placeholder)
 - Dice Demo (runs the dice demo inline)
 - Audio Settings
 - Change Song
 - Quit
"""

import os
import sys
import json
import time
import math
import pygame
import random
from typing import Optional
from audio.audio import AudioManager
from ui.start_menu import StartMenu, _make_vignette
from ui.change_song_menu import ChangeSongMenu
from ui.audio_settings import AudioSettingsMenu
from ui.keybindings_menu import KeybindingsMenu
from ui.achievements_menu import AchievementsMenu
from ui.shop_menu import ShopMenu
from ui.consumables_menu import ConsumablesMenu
from ui.status_display import StatusDisplay
from cards.card import create_dice_rolls
from game.game_engine import GameManager
from settings import Settings
from items import registry
from replay_system import GameReplay
from stats_tracker import StatsTracker
from theme_system import ThemeManager


BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.json')

# Cache for pre-rendered die sprites: {(size, face): Surface}
DIE_SPRITE_CACHE = {}

# Particle system for dice trails
class DiceParticle:
    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.uniform(2, 5)
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 600 * dt  # gravity
        self.vx *= 0.98  # air resistance
        self.lifetime -= dt
        return self.lifetime > 0
    
    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = int(self.size * (self.lifetime / self.max_lifetime))
        if size > 0:
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
            surface.blit(s, (int(self.x - size), int(self.y - size)))

# Attempt to import the achievement notifier. If running with a different
# cwd or from the package root, ensure the package path is available.
try:
    from graphics.achivments import notifier
except Exception:
    # If import fails (e.g. running from inside the uno_game folder),
    # add the package parent directory to sys.path and retry.
    parent = os.path.abspath(os.path.join(BASE_DIR, '..'))
    if parent not in sys.path:
        sys.path.insert(0, parent)
    try:
        from graphics.achivments import notifier
    except Exception:
        # As a last resort, create a dummy notifier that no-ops so calls
        # to notifier.show()/update()/draw() won't crash at runtime.
        class _DummyNotifier:
            def show(self, *a, **k):
                return
            def update(self, *a, **k):
                return
            def draw(self, *a, **k):
                return

        notifier = _DummyNotifier()


def load_settings():
    defaults = {'music_file': 'test.mp3', 'music_volume': 0.6, 'sfx_volume': 1.0}
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                defaults.update(data)
    except Exception:
        pass
    return defaults


def save_settings(data: dict):
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def _render_die_sprite(size: int, face: int) -> pygame.Surface:
    """Render a single die face with layered shading and cached result.

    Visual goals (matching upgraded chips style):
      - Soft drop shadow
      - Beveled rim with gradient (light top-left, darker bottom-right)
      - Subtle radial glow toward center
      - Gloss highlight on upper-left quadrant
      - Pips with inner shadow + micro highlight
    """
    key = (size, face)
    if key in DIE_SPRITE_CACHE:
        return DIE_SPRITE_CACHE[key]

    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, size, size)
    border_radius = max(4, size // 7)

    # 1. Drop shadow (below face)
    shadow = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 55), (size * 0.10, size * 0.72, size * 0.80, size * 0.26))
    surf.blit(shadow, (0, 0))

    # 2. Base face fill
    base_col = (245, 245, 246)
    pygame.draw.rect(surf, base_col, rect, border_radius=border_radius)

    # 3. Rim / bevel gradient by inflating rect inward
    rim_layers = max(5, size // 14)
    for i in range(rim_layers):
        t = i / rim_layers
        # Light bias top-left, darker toward bottom-right
        shade = 255 - int(28 * t)
        col = (shade, shade, shade - 4)
        inset = rect.inflate(-i * 2, -i * 2)
        if inset.width <= 0 or inset.height <= 0:
            break
        pygame.draw.rect(surf, col, inset, border_radius=max(1, border_radius - i))

    # 4. Inner face panel slightly cooler tone
    inner = rect.inflate(-size * 0.14, -size * 0.14)
    pygame.draw.rect(surf, (228, 230, 233), inner, border_radius=max(2, border_radius - 3))

    # 5. Radial center glow (additive)
    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size / 2, size / 2
    max_r = size * 0.48
    steps = 18
    for j in range(steps):
        rt = j / steps
        radius = max_r * (1 - rt * 0.85)
        alpha = int(42 * (1 - rt) ** 1.8)
        col = (255, 255, 255, alpha)
        pygame.draw.circle(glow, col, (int(cx), int(cy)), int(radius))
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # 6. Directional highlight (upper-left) & shade (lower-right)
    hl = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(hl, (255, 255, 255, 48), (0, 0, size, size * 0.55), border_radius=border_radius)
    surf.blit(hl, (0, 0))
    shade = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(shade, (0, 0, 0, 28), (0, size * 0.55, size, size * 0.50), border_radius=border_radius)
    surf.blit(shade, (0, 0))

    # 7. Pips with rim, inner shadow, tiny gloss spot
    def pip(cx, cy, r):
        # Pip drop shadow
        pygame.draw.circle(surf, (0, 0, 0, 100), (int(cx + r * 0.22), int(cy + r * 0.22)), r)
        # Main pip body
        pygame.draw.circle(surf, (18, 18, 20), (int(cx), int(cy)), r)
        inner_r = max(1, r - 2)
        pygame.draw.circle(surf, (40, 40, 42), (int(cx), int(cy)), inner_r)
        # Gloss
        gloss_r = max(1, r // 3)
        pygame.draw.circle(surf, (255, 255, 255, 90), (int(cx - r * 0.35), int(cy - r * 0.35)), gloss_r)

    col_1 = size * 0.22
    col_2 = size * 0.50
    col_3 = size * 0.78
    row_1 = size * 0.22
    row_2 = size * 0.50
    row_3 = size * 0.78
    pr = max(3, size // 11)

    if face in (1, 3, 5):
        pip(col_2, row_2, pr)
    if face in (2, 3, 4, 5, 6):
        pip(col_1, row_1, pr)
        pip(col_3, row_3, pr)
    if face in (4, 5, 6):
        pip(col_3, row_1, pr)
        pip(col_1, row_3, pr)
    if face == 6:
        pip(col_1, row_2, pr)
        pip(col_3, row_2, pr)

    # 8. Outer border
    pygame.draw.rect(surf, (32, 32, 34), rect, 1, border_radius=border_radius)

    DIE_SPRITE_CACHE[key] = surf
    return surf


def draw_die(surface: pygame.Surface, x: int, y: int, size: int, value: int):
    # Use pre-rendered sprite if available; otherwise generate on-the-fly
    try:
        spr = _render_die_sprite(size, value)
        surface.blit(spr, (int(x), int(y)))
    except Exception:
        # fallback simple draw
        rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(surface, (255, 255, 255), rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)
        # simple pips
        def pip(cx, cy):
            pygame.draw.circle(surface, (0, 0, 0), (int(cx), int(cy)), size // 10)
        col_1 = x + size * 0.25
        col_2 = x + size * 0.5
        col_3 = x + size * 0.75
        row_1 = y + size * 0.25
        row_2 = y + size * 0.5
        row_3 = y + size * 0.75
        if value in (1, 3, 5):
            pip(col_2, row_2)
        if value in (2, 3, 4, 5, 6):
            pip(col_1, row_1)
            pip(col_3, row_3)
        if value in (4, 5, 6):
            pip(col_3, row_1)
            pip(col_1, row_3)
        if value == 6:
            pip(col_1, row_2)
            pip(col_3, row_2)


def draw_die_flipping(surface: pygame.Surface, x: int, y: int, size: int, from_val: int, to_val: int, progress: float, particles=None):
    """Draw a die with realistic physics: 3D tumbling, bounce with deceleration, and particle trails.
    
    Enhanced physics:
    - Multiple bounces with decreasing amplitude
    - Velocity-based rotation (faster spin at start, slows down)
    - 3D perspective scaling (die appears closer/further)
    - Particle trail emission during movement
    - Impact deformation on bounce
    """
    p = max(0.0, min(1.0, progress))
    
    # Physics-based bounce with multiple rebounds
    def realistic_bounce(t):
        # Simulate multiple bounces with damping
        if t < 0.3:  # Initial toss
            phase = t / 0.3
            return math.sin(phase * math.pi) * 1.2
        elif t < 0.55:  # First bounce
            phase = (t - 0.3) / 0.25
            return math.sin(phase * math.pi) * 0.6
        elif t < 0.75:  # Second bounce
            phase = (t - 0.55) / 0.2
            return math.sin(phase * math.pi) * 0.25
        elif t < 0.9:  # Final settle bounce
            phase = (t - 0.75) / 0.15
            return math.sin(phase * math.pi) * 0.08
        else:  # Settled
            return 0.0
    
    # Velocity curve (fast at start, decelerates)
    velocity = (1 - p) ** 1.5
    
    # Height with realistic bounce physics
    bounce_height = realistic_bounce(p) * size * 1.5
    y_offset = int(-bounce_height)
    
    # Rotation based on velocity (tumbling slows as it settles)
    rotation_speed = 1080 * velocity + 360 * p  # Starts fast, adds base rotation
    rotation = rotation_speed * p
    
    # 3D perspective: scale based on height (appears larger when higher)
    height_scale = 1.0 + (bounce_height / (size * 3.0)) * 0.4
    
    # Impact squash on bounce (squash when hitting ground)
    squash = 1.0
    if p > 0.28 and p < 0.32:  # First impact
        impact_progress = (p - 0.28) / 0.04
        squash = 1.0 - 0.15 * math.sin(impact_progress * math.pi)
    elif p > 0.53 and p < 0.56:  # Second impact
        impact_progress = (p - 0.53) / 0.03
        squash = 1.0 - 0.08 * math.sin(impact_progress * math.pi)
    
    # Emit particles during fast movement
    if particles is not None and velocity > 0.3 and random.random() < 0.4:
        trail_colors = [(255, 255, 255), (240, 240, 250), (220, 220, 240)]
        for _ in range(random.randint(1, 3)):
            px = x + size/2 + random.uniform(-size*0.3, size*0.3)
            py = y + size/2 + y_offset + random.uniform(-size*0.2, size*0.2)
            vx = random.uniform(-50, 50)
            vy = random.uniform(-80, -20)
            particles.append(DiceParticle(px, py, vx, vy, random.choice(trail_colors), random.uniform(0.3, 0.8)))
    
    # Face selection with rapid changes during tumble
    tumble_speed = int(rotation / 90)  # Change face every 90 degrees
    if p < 0.85:  # Still tumbling
        face_sequence = [from_val, random.randint(1, 6), random.randint(1, 6), to_val]
        face = face_sequence[tumble_speed % len(face_sequence)]
    else:  # Settled on final value
        face = to_val if to_val else random.randint(1, 6)
    
    # 3D rotation effects: squash horizontally based on rotation angle
    angle_rad = math.radians(rotation % 360)
    scale_x = abs(math.cos(angle_rad)) * height_scale
    scale_y = height_scale * squash
    
    w = max(6, int(size * scale_x))
    h = int(size * scale_y)

    # Render the sprite for the current face
    sprite = _render_die_sprite(size, face)

    # Apply 3D perspective scaling
    if w != size or h != size:
        sprite = pygame.transform.scale(sprite, (w, h))

    # Rotate the sprite with velocity-based tumbling
    if rotation != 0:
        sprite = pygame.transform.rotate(sprite, rotation)

    # Dynamic shadow with realistic properties
    shadow_alpha = int(120 * (1 - bounce_height / (size * 2)))  # Darker when closer to ground
    shadow_size = int(size * (1 + bounce_height / (size * 4)))  # Larger when higher
    shadow_blur = int(bounce_height / 5) + 2  # More blur when higher
    
    # Multi-layer shadow for soft blur effect
    shadow_surf = pygame.Surface((shadow_size + shadow_blur*4, size // 2 + shadow_blur*2), pygame.SRCALPHA)
    for blur_layer in range(shadow_blur):
        alpha = shadow_alpha // (blur_layer + 2)
        blur_size = shadow_size + blur_layer * 2
        ellipse_rect = pygame.Rect(shadow_blur*2 - blur_layer, shadow_blur - blur_layer//2, blur_size, size // 2 + blur_layer)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, alpha), ellipse_rect)
    
    surface.blit(shadow_surf, (int(x - shadow_blur*2), int(y + size - shadow_blur)))

    # Motion blur effect during fast movement
    if velocity > 0.5:
        blur_alpha = int(60 * velocity)
        blur_sprite = sprite.copy()
        blur_sprite.set_alpha(blur_alpha)
        blur_offset = int(velocity * 8)
        blur_rect = blur_sprite.get_rect(center=(int(x + size / 2 - blur_offset), int(y + size / 2 + y_offset - blur_offset//2)))
        surface.blit(blur_sprite, blur_rect)

    # Draw the main die
    die_rect = sprite.get_rect(center=(int(x + size / 2), int(y + size / 2 + y_offset)))
    surface.blit(sprite, die_rect)
    
    # Glint effect on settling
    if p > 0.88 and p < 0.95:
        glint_progress = (p - 0.88) / 0.07
        glint_alpha = int(180 * math.sin(glint_progress * math.pi))
        glint_size = int(size * 0.3)
        glint_surf = pygame.Surface((glint_size*2, glint_size*2), pygame.SRCALPHA)
        pygame.draw.circle(glint_surf, (255, 255, 255, glint_alpha), (glint_size, glint_size), glint_size)
        surface.blit(glint_surf, (int(x + size*0.2), int(y + y_offset + size*0.2)), special_flags=pygame.BLEND_RGBA_ADD)


def run_dice_demo(screen: pygame.Surface, audio: AudioManager, num_dice: int = 10):
    clock = pygame.time.Clock()
    running = True
    rolls = create_dice_rolls(num_dice)
    font = pygame.font.SysFont('Arial', 20)

    # try to play a roll sfx when rolling
    sfx_name = 'mouse-click-290204.mp3'  # included asset
    # (background renderer removed - using flat fill to match previous behavior)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Start a short roll animation, then set final rolls
                    final_rolls = create_dice_rolls(num_dice)
                    try:
                        audio.play_sound_effect(sfx_name, volume=0.8)
                    except Exception:
                        pass

                    anim_start = pygame.time.get_ticks()
                    anim_duration = 700  # ms
                    anim_running = True
                    # sample a 'from' face per die (current value or random)
                    from_faces = [d.get('value', random.randint(1,6)) for d in rolls]

                    while anim_running:
                        now = pygame.time.get_ticks()
                        elapsed = now - anim_start
                        progress = min(1.0, elapsed / anim_duration)

                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                anim_running = False

                        # draw background (flat fill)
                        screen.fill((30, 140, 40))

                        # layout dice in two rows of up to 5
                        die_size = 80
                        die_spacing = 100
                        total_width = 5 * die_size + 4 * (die_spacing - die_size)
                        start_x = (screen.get_width() - total_width) // 2
                        top_y = 100
                        bottom_y = 220

                        for i, d in enumerate(final_rolls):
                            if i < 5:
                                x = start_x + i * die_spacing
                                y = top_y
                            else:
                                x = start_x + (i - 5) * die_spacing
                                y = bottom_y
                            # stagger per-die progress slightly for a nicer feel
                            stagger = (i % 5) * 0.03
                            p = min(1.0, max(0.0, (progress - stagger) / (1.0 - stagger)))
                            draw_die_flipping(screen, x, y, die_size, from_faces[i], d.get('value', 0), p)

                        font = pygame.font.SysFont('Arial', 20)
                        txt = font.render(f"Rolling...", True, (255, 255, 255))
                        screen.blit(txt, (20, 20))

                        pygame.display.flip()
                        pygame.time.delay(16)

                        if progress >= 1.0:
                            anim_running = False

                    # commit final values after animation
                    rolls = final_rolls
                elif event.key == pygame.K_k:
                    # Demo achievement popup for testing (appears bottom-left)
                    try:
                        notifier.show(
                            "Demo Achievement",
                            "This verifies popups appear bottom-left",
                            image_path=os.path.join(ASSETS_DIR, 'ach_demo.png'),
                            placement='bottom-right'
                        )
                    except Exception:
                        pass
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # draw background
            # draw background (flat fill)
            screen.fill((30, 140, 40))

        # layout dice in two rows of up to 5
        die_size = 80
        die_spacing = 100
        total_width = 5 * die_size + 4 * (die_spacing - die_size)
        start_x = (screen.get_width() - total_width) // 2
        top_y = 100
        bottom_y = 220

        for i, d in enumerate(rolls):
            if i < 5:
                x = start_x + i * die_spacing
                y = top_y
            else:
                x = start_x + (i - 5) * die_spacing
                y = bottom_y
            draw_die(screen, x, y, die_size, d.get('value', 0))

        total = sum(d.get('value', 0) for d in rolls)
        txt = font.render(f"Roll total: {total}    (R to roll, Esc to return)", True, (255, 255, 255))
        screen.blit(txt, (20, 20))

        vals = ', '.join(str(d.get('value', '?')) for d in rolls)
        txt2 = font.render("Values: " + vals, True, (255, 255, 255))
        screen.blit(txt2, (20, 50))

        pygame.display.flip()
        clock.tick(60)


def show_loading_screen(screen: pygame.Surface, duration: float = 2.0):
    """Display a loading screen with backgammon board background and animated progress.
    
    Args:
        screen: The pygame surface to draw on
        duration: How long to show the loading screen (seconds)
    """
    from ui.loading_screen import LoadingScreen
    
    # Create a dedicated loading screen
    loader = LoadingScreen(
        title='Loading Game...',
        subtitle='Preparing your game session',
        duration=duration
    )
    
    # Run the loading screen (it will auto-close after duration)
    loader.run(screen)


def player_setup(screen: pygame.Surface):
    """Pre-game form with clickable buttons, caret blinking, and a scrollable players list.

    Returns (player_names, starting_chips) or None if cancelled.
    """
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 20)

    input_text = ''
    players = []
    starting_chips = 20  # fixed per requirement
    # Styling & state
    felt_color = (12, 80, 34)
    vignette = _make_vignette(screen.get_width(), screen.get_height())
    # (background renderer removed for player setup)
    # spotlight removed for cleaner look
    spotlight_center = [screen.get_width() // 2, 80]
    selected_idx: Optional[int] = None
    max_name_len = 16

    # Button rectangles
    btn_w, btn_h = 100, 36
    add_btn = pygame.Rect(20, 420, btn_w, btn_h)
    remove_btn = pygame.Rect(140, 420, btn_w, btn_h)
    start_btn = pygame.Rect(260, 420, btn_w, btn_h)
    cancel_btn = pygame.Rect(380, 420, btn_w, btn_h)

    error_msg = ''
    scroll_offset = 0
    caret_visible = True
    last_blink = pygame.time.get_ticks()
    blink_interval = 500

    def draw_button(rect, text):
        # pill-style button with gold rim and darker hover
        rim = (212, 175, 55)
        inner = (60, 60, 60)
        hover_inner = (90, 90, 90)
        mx, my = pygame.mouse.get_pos()
        is_hover = rect.collidepoint((mx, my))
        pygame.draw.rect(screen, rim, rect, border_radius=12)
        inner_col = hover_inner if is_hover else inner
        inner_rect = rect.inflate(-6, -6)
        pygame.draw.rect(screen, inner_col, inner_rect, border_radius=10)
        txt = font.render(text, True, (245, 245, 245))
        tr = txt.get_rect(center=rect.center)
        screen.blit(txt, tr)

    while True:
        now = pygame.time.get_ticks()
        if now - last_blink >= blink_interval:
            caret_visible = not caret_visible
            last_blink = now

        mx, my = pygame.mouse.get_pos()
        mouse_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pressed = True
            elif event.type == pygame.MOUSEWHEEL:
                # mouse wheel scroll
                max_off = max(0, len(players) - 8)
                scroll_offset = min(max_off, max(0, scroll_offset - event.y))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    if input_text.strip():
                        name = input_text.strip()[:max_name_len]
                        # Validate name
                        if not name:
                            error_msg = 'Name cannot be empty'
                            try:
                                from audio.audio import AudioManager
                                temp_audio = AudioManager(audio_folder=ASSETS_DIR)
                                temp_audio.play_sound_effect('cubes.mp3', volume=0.4)  # Error sound
                            except Exception:
                                pass
                        elif len(name) < 2:
                            error_msg = 'Name must be at least 2 characters'
                            try:
                                from audio.audio import AudioManager
                                temp_audio = AudioManager(audio_folder=ASSETS_DIR)
                                temp_audio.play_sound_effect('cubes.mp3', volume=0.4)  # Error sound
                            except Exception:
                                pass
                        elif not any(c.isalnum() for c in name):
                            error_msg = 'Name must contain letters or numbers'
                            try:
                                from audio.audio import AudioManager
                                temp_audio = AudioManager(audio_folder=ASSETS_DIR)
                                temp_audio.play_sound_effect('cubes.mp3', volume=0.4)  # Error sound
                            except Exception:
                                pass
                        elif name in players:
                            error_msg = 'Name already used'
                            try:
                                from audio.audio import AudioManager
                                temp_audio = AudioManager(audio_folder=ASSETS_DIR)
                                temp_audio.play_sound_effect('cubes.mp3', volume=0.4)  # Error sound
                            except Exception:
                                pass
                        else:
                            players.append(name)
                            input_text = ''
                            error_msg = ''
                            selected_idx = len(players) - 1
                            # Play success sound (import audio if needed)
                            try:
                                from audio.audio import AudioManager
                                temp_audio = AudioManager(audio_folder=ASSETS_DIR)
                                temp_audio.play_sound_effect('mouse-click-290204.mp3', volume=0.5)
                            except Exception:
                                pass
                elif event.key == pygame.K_BACKSPACE:
                    if input_text:
                        input_text = input_text[:-1]
                    elif players:
                        # remove selected if present, else pop last
                        if selected_idx is not None and 0 <= selected_idx < len(players):
                            players.pop(selected_idx)
                            # adjust selection
                            if not players:
                                selected_idx = None
                            else:
                                selected_idx = max(0, min(selected_idx, len(players) - 1))
                        else:
                            players.pop()
                elif event.key == pygame.K_UP:
                    # move selection up in list
                    if players:
                        if selected_idx is None:
                            selected_idx = 0
                        else:
                            selected_idx = max(0, selected_idx - 1)
                        if selected_idx < scroll_offset:
                            scroll_offset = selected_idx
                elif event.key == pygame.K_DOWN:
                    if players:
                        if selected_idx is None:
                            selected_idx = 0
                        else:
                            selected_idx = min(len(players) - 1, selected_idx + 1)
                        max_off = max(0, len(players) - 8)
                        if selected_idx >= scroll_offset + 8:
                            scroll_offset = min(max_off, selected_idx - 7)
                else:
                    ch = event.unicode
                    if ch and ch.isprintable():
                        if len(input_text) < max_name_len:
                            input_text += ch

        # Handle button clicks and list selection
        players_start_y = 192
        visible_count = 8
        if mouse_pressed:
            # check if clicked in players list area
            if mx >= 20 and mx <= screen.get_width() - 20 and my >= players_start_y and my < players_start_y + visible_count * 24:
                idx = scroll_offset + (my - players_start_y) // 24
                if 0 <= idx < len(players):
                    selected_idx = idx
            elif add_btn.collidepoint((mx, my)):
                if input_text.strip():
                    name = input_text.strip()[:max_name_len]
                    if name in players:
                        error_msg = 'Name already used'
                    else:
                        players.append(name)
                        input_text = ''
                        error_msg = ''
                        selected_idx = len(players) - 1
            elif remove_btn.collidepoint((mx, my)):
                if players:
                    if selected_idx is not None and 0 <= selected_idx < len(players):
                        players.pop(selected_idx)
                        if not players:
                            selected_idx = None
                        else:
                            selected_idx = max(0, min(selected_idx, len(players) - 1))
                    else:
                        players.pop()
            elif start_btn.collidepoint((mx, my)):
                if len(players) < 2:
                    error_msg = 'Need at least 2 players'
                else:
                    return players, starting_chips
            elif cancel_btn.collidepoint((mx, my)):
                return None

        # Draw UI (polished)
        screen.fill(felt_color)
        # vignette
        try:
            screen.blit(vignette, (0, 0))
        except Exception:
            pass
        y = 20
        title = font.render('Pre-game Setup', True, (255, 255, 255))
        screen.blit(title, (20, y))
        y += 36

        instr = font.render("Type a name then click Add (or press Enter).", True, (230, 230, 230))
        screen.blit(instr, (20, y))
        y += 30

        chips_txt = font.render(f'Starting chips (fixed): {starting_chips}', True, (255, 255, 255))
        screen.blit(chips_txt, (20, y))
        y += 30

        # Input box (styled)
        input_box = pygame.Rect(20, y, 360, 40)
        pygame.draw.rect(screen, (212, 175, 55), input_box, border_radius=8)
        inner = input_box.inflate(-6, -6)
        pygame.draw.rect(screen, (40, 40, 40), inner, border_radius=6)
        if input_text:
            input_surf = font.render(input_text, True, (245, 245, 245))
        else:
            input_surf = font.render('Type player name…', True, (160, 160, 160))
        screen.blit(input_surf, (input_box.x + 8, input_box.y + 8))
        y += 50

        # Players list (scrollable)
        pl_title = font.render('Players:', True, (255, 255, 255))
        screen.blit(pl_title, (20, y))
        y += 26
        visible_count = 8
        max_off = max(0, len(players) - visible_count)
        scroll_offset = max(0, min(scroll_offset, max_off))
        start_idx = scroll_offset
        end_idx = min(len(players), start_idx + visible_count)
        # draw selectable player rows
        row_x = 40
        row_w = screen.get_width() - 80
        for i, p in enumerate(players[start_idx:end_idx], start=start_idx):
            row_rect = pygame.Rect(row_x - 8, y - 2, row_w + 16, 24)
            if selected_idx == i:
                # highlight selected with translucent gold
                highlight = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
                highlight.fill((212, 175, 55, 48))
                screen.blit(highlight, (row_rect.x, row_rect.y))
            ptxt = font.render('- ' + p, True, (240, 240, 240))
            screen.blit(ptxt, (row_x, y))
            y += 24

        # small scrollbar indicator if needed
        if len(players) > visible_count:
            bar_h = visible_count * 20
            bar_x = 10
            bar_y = 120
            pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, 6, bar_h))
            thumb_h = max(12, int(bar_h * (visible_count / len(players))))
            thumb_y = bar_y + int((bar_h - thumb_h) * (scroll_offset / max_off)) if max_off else bar_y
            pygame.draw.rect(screen, (120, 120, 120), (bar_x, thumb_y, 6, thumb_h))

        # caret
        if caret_visible and input_text:
            caret_x = input_box.x + 8 + input_surf.get_width()
            caret_y1 = input_box.y + 8
            caret_y2 = input_box.y + input_box.height - 8
            pygame.draw.line(screen, (245, 245, 245), (caret_x, caret_y1), (caret_x, caret_y2), 2)

        # Draw buttons
        draw_button(add_btn, 'Add')
        draw_button(remove_btn, 'Remove')
        draw_button(start_btn, 'Start')
        draw_button(cancel_btn, 'Cancel')

        # Error message
        if error_msg:
            em = font.render(error_msg, True, (255, 100, 100))
            screen.blit(em, (20, 300))

        # spotlight removed — kept vignette only for subtle focus

        pygame.display.flip()
        clock.tick(60)


def run_game_engine(screen: pygame.Surface, audio: AudioManager):
    """Runs the Zanzibar GameManager in interactive mode inside the pygame window.

    Controls:
    - Space: Play next round
    - I: Open inventory/consumables menu
    - S: Open shop menu
    - Esc: Return to menu
    """
    # Isaiah NPC pixel art (left side) -- only shown during setup, not in main gameplay
    isaiah_npc = None
    isaiah_states = []
    isaiah_state_idx = 0
    clock = pygame.time.Clock()
    
    # Responsive scaling based on window size
    def scale_ui(base_size, ref_width=900):
        """Scale UI element based on current window width."""
        return int(base_size * (screen.get_width() / ref_width))
    
    font_size = scale_ui(20)
    header_font_size = scale_ui(18)
    
    # Cached surfaces (performance optimization)
    cached_vignette = None
    cached_felt_texture = None
    cached_fonts = {}
    
    def get_font(size, bold=False):
        """Get a cached font with current accessibility settings."""
        font_family = 'Comic Sans MS' if dyslexia_font_mode else 'Arial'
        key = ('general', size, bold, dyslexia_font_mode)
        if key not in cached_fonts:
            cached_fonts[key] = pygame.font.SysFont(font_family, size, bold=bold)
        return cached_fonts[key]
    
    # Accessibility options
    high_contrast_mode = False
    dyslexia_font_mode = False
    
    # Particle system for dice effects
    dice_particles = []
    
    # Initialize systems
    theme_manager = ThemeManager(SETTINGS_PATH)
    replay_system = GameReplay(os.path.join(BASE_DIR, 'replays'))
    stats_tracker = StatsTracker(os.path.join(BASE_DIR, 'stats.json'))

    # For simplicity, player names and starting chips are provided before starting
    # the engine via a small pre-game form.
    setup = player_setup(screen)
    if not setup:
        return
    player_names, starting_chips = setup
    # Isaiah NPC is not shown after setup
    isaiah_npc = None
    # Fade out before loading screen
    from ui.ui_utils import fade_transition
    fade_transition(screen, duration=0.3, fade_out=True)
    # Show loading screen while preparing game
    show_loading_screen(screen, duration=2.5)
    # Fade in after loading
    fade_transition(screen, duration=0.3, fade_out=False)
    gm = GameManager(player_names, starting_chips, screen=screen)
    
    # Initialize game settings for keybindings
    game_settings = Settings()

    # UI state
    running = True
    orig_size = screen.get_size()
    is_fullscreen = False
    round_message = None
    round_message_end = 0.0
    # no animation: show improved 3D dice immediately when a round is played
    anim_duration = 0.8
    # Dice roll animation state (for in-engine round rolls)
    roll_anim_active = False
    roll_anim_start_ms = 0
    roll_anim_total_ms = 900
    # Mapping player -> list of faces transitioning to final roll
    roll_anim_from: dict[str, list[int]] = {}
    
    # Track current player (for shop/inventory)
    current_player_idx = 0
    
    # Menu states
    show_inventory = False
    show_shop = False
    show_settings_overlay = False
    show_stats_overlay = False
    show_replay_browser = False
    show_theme_menu = False
    # Replay playback state
    replay_playing = False
    replay_paused = True
    replay_playback_timer = 0.0
    replay_playback_index = 0
    current_replay_info = None
    
    # Initialize status display
    status_display = StatusDisplay()
    # Start recording the session
    try:
        replay_system.start_recording(player_names, starting_chips)
        stats_tracker.record_game_start(player_names)
    except Exception:
        pass
    
    while running:
        # frame timing
        ms = clock.tick(60)
        dt = ms / 1000.0

        frame_changed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Prioritize overlay interactions
                if show_theme_menu:
                    # Theme menu: number keys select themes, Esc closes
                    if event.key in (pygame.K_ESCAPE, pygame.K_m):
                        show_theme_menu = False
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                                       pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9):
                        idx = (event.key - pygame.K_1)
                        themes = theme_manager.list_themes()
                        if 0 <= idx < len(themes):
                            key_name = themes[idx][0]
                            theme_manager.set_theme(key_name)
                            notifier.show('Theme Applied', f"{themes[idx][1]}")
                            show_theme_menu = False
                    # consume overlay event
                    continue
                if show_replay_browser:
                    # Replay browser interactions
                    if event.key in (pygame.K_ESCAPE, pygame.K_l):
                        show_replay_browser = False
                        # stop any playback
                        replay_playing = False
                        replay_paused = True
                        replay_playback_timer = 0.0
                        replay_playback_index = 0
                        current_replay_info = None
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                                       pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9):
                        idx = (event.key - pygame.K_1)
                        replays = replay_system.list_replays()
                        if 0 <= idx < len(replays):
                            filepath = replays[idx]['filepath']
                            if replay_system.load_replay(filepath):
                                replay_playing = True
                                replay_paused = True
                                replay_playback_timer = 0.0
                                replay_playback_index = 0
                                current_replay_info = replays[idx]
                                notifier.show('Replay Loaded', replays[idx]['filename'])
                    elif event.key == pygame.K_SPACE:
                        # Toggle play/pause when a replay is loaded
                        if replay_system.playback_data is not None:
                            replay_paused = not replay_paused
                            replay_playing = not replay_paused
                    elif event.key == pygame.K_RIGHT:
                        # Step forward one event
                        if replay_system.playback_data is not None:
                            ev = replay_system.get_next_event()
                            if ev:
                                notifier.show('Replay Event', f"{ev.get('type')}: {str(ev.get('data'))[:80]}")
                    # consume overlay event
                    continue
                if show_stats_overlay:
                    # Close stats overlay with Tab or Esc
                    if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
                        show_stats_overlay = False
                        continue
                # Normal key handling
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_f, pygame.K_F11):
                    # toggle fullscreen
                    try:
                        if not is_fullscreen:
                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            is_fullscreen = True
                        else:
                            screen = pygame.display.set_mode(orig_size)
                            is_fullscreen = False
                    except Exception:
                        pass
                elif event.key == pygame.K_k:
                    # Demo achievement popup for testing (appears bottom-left)
                    try:
                        notifier.show(
                            "Demo Achievement",
                            "This verifies popups appear bottom-left",
                            image_path=os.path.join(ASSETS_DIR, 'ach_demo.png'),
                            placement='bottom-left'
                        )
                    except Exception:
                        pass
                elif event.key == pygame.K_i:
                    # Open inventory menu (correct key per header/help text)
                    show_inventory = True
                elif event.key == pygame.K_s:
                    # Open shop menu
                    show_shop = True
                elif event.key == pygame.K_o:
                    # Toggle settings overlay
                    show_settings_overlay = not show_settings_overlay
                elif event.key == pygame.K_TAB:
                    # Quick open stats overview
                    show_stats_overlay = not show_stats_overlay
                elif event.key == pygame.K_l:
                    # Open replay browser (L for 'replays')
                    show_replay_browser = not show_replay_browser
                elif event.key == pygame.K_m:
                    # Theme menu (M)
                    show_theme_menu = not show_theme_menu
                    # Switch current player
                    current_player_idx = (current_player_idx + 1) % len(player_names)
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                    # Quick use item from inventory
                    key_map = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4}
                    slot = key_map[event.key]
                    current_player = player_names[current_player_idx]
                    player_data = gm.players[current_player]
                    if 'inventory' in player_data and player_data['inventory']:
                        items_list = list(player_data['inventory'].get_all_items().items())
                        if slot < len(items_list):
                            item_name, qty = items_list[slot]
                            if gm.use_item(current_player, item_name):
                                try:
                                    audio.play_sound_effect('whoosh.mp3', volume=0.5)
                                except Exception:
                                    pass
                elif event.key == pygame.K_SPACE:
                    # Trigger dice roll animation transitioning to new round result
                    # Play roll start whoosh
                    try:
                        audio.play_sound_effect('whoosh.mp3', volume=0.4)
                    except Exception:
                        pass
                    # Schedule dice bounce sound mid-animation
                    try:
                        audio.play_sound_effect('dice_bounce.mp3', volume=0.6)
                    except Exception:
                        pass
                    # Capture previous shown faces per player (random if none)
                    roll_anim_from.clear()
                    for name in gm.player_order:
                        existing = gm.round_results.get(name, {}).get('final_roll') or [random.randint(1,6) for _ in range(3)]
                        # shuffle to look different prior to final
                        roll_anim_from[name] = [random.randint(1,6) for _ in existing]
                    # Compute new round results immediately (logic not delayed)
                    try:
                        gm.play_round()
                    except Exception:
                        pass
                    roll_anim_start_ms = pygame.time.get_ticks()
                    roll_anim_active = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                # isaiah_npc is only available during setup; guard access to avoid
                # AttributeError when it's None (clicks were closing the game).
                if isaiah_npc is not None:
                    try:
                        npc_rect = pygame.Rect(isaiah_npc.pos[0], isaiah_npc.pos[1], isaiah_npc.size, isaiah_npc.size)
                        if npc_rect.collidepoint(mx, my):
                            isaiah_state_idx = (isaiah_state_idx + 1) % len(isaiah_states)
                            isaiah_npc.set_state(isaiah_states[isaiah_state_idx])
                            frame_changed = True
                    except Exception:
                        # Swallow any unexpected errors from npc structure
                        pass

        # If the game manager signalled the game ended (winner found), exit the
        # engine loop so control returns to the Start Menu instead of quitting.
        if getattr(gm, '_end_game', False):
            running = False
            continue
        
        # Handle inventory menu
        if show_inventory:
            current_player = player_names[current_player_idx]
            player_data = gm.players[current_player]
            
            # Initialize inventory if not present
            if 'inventory' not in player_data or player_data['inventory'] is None:
                from items import Inventory
                player_data['inventory'] = Inventory()
            
            inventory_menu = ConsumablesMenu(screen, player_data['inventory'])
            
            # Get items as ConsumableItem objects
            items = []
            for item_name, quantity in player_data['inventory'].get_all_items().items():
                item = registry.get_item(item_name)
                if item and quantity > 0:
                    items.append(item)
            
            if items:
                inventory_menu.selected_item = items[0]
            
            inv_running = True
            while inv_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            inv_running = False
                        elif event.key == pygame.K_RETURN and inventory_menu.selected_item:
                            # Use the selected item
                            if gm.use_item(current_player, inventory_menu.selected_item.name):
                                # Play use item sound
                                try:
                                    audio.play_sound_effect('whoosh.mp3', volume=0.5)
                                except Exception:
                                    pass
                                # Refresh items list
                                items = []
                                for item_name, quantity in player_data['inventory'].get_all_items().items():
                                    item = registry.get_item(item_name)
                                    if item and quantity > 0:
                                        items.append(item)
                                # Update selected item
                                if items:
                                    inventory_menu.selected_item = items[0]
                                else:
                                    inventory_menu.selected_item = None
                        elif event.key == pygame.K_UP:
                            if items and inventory_menu.selected_item:
                                idx = items.index(inventory_menu.selected_item)
                                if idx > 0:
                                    inventory_menu.selected_item = items[idx - 1]
                                    if idx - 1 < inventory_menu.scroll_offset:
                                        inventory_menu.scroll_offset = idx - 1
                                    # Navigation sound
                                    try:
                                        audio.play_sound_effect('mouse-click-290204.mp3', volume=0.3)
                                    except Exception:
                                        pass
                            elif items:
                                inventory_menu.selected_item = items[0]
                        elif event.key == pygame.K_DOWN:
                            if items and inventory_menu.selected_item:
                                idx = items.index(inventory_menu.selected_item)
                                if idx < len(items) - 1:
                                    inventory_menu.selected_item = items[idx + 1]
                                    # Navigation sound
                                    try:
                                        audio.play_sound_effect('mouse-click-290204.mp3', volume=0.3)
                                    except Exception:
                                        pass
                                    if idx + 1 >= inventory_menu.scroll_offset + inventory_menu.max_items_shown:
                                        inventory_menu.scroll_offset = idx + 1 - inventory_menu.max_items_shown + 1
                            elif items:
                                inventory_menu.selected_item = items[0]
                
                screen.fill((20, 20, 30))
                if not items:
                    # Show empty inventory message
                    empty_font = pygame.font.SysFont('Arial', 24)
                    msg = empty_font.render("Inventory is empty! Press S to shop.", True, (220, 220, 220))
                    msg_rect = msg.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
                    screen.blit(msg, msg_rect)
                else:
                    inventory_menu.draw(items)
                # draw any queued achievement popups (non-blocking)
                try:
                    notifier.update()
                    notifier.draw(screen)
                except Exception:
                    pass
                pygame.display.flip()
                clock.tick(60)
            
            show_inventory = False
        
        # Handle shop menu
        if show_shop:
            current_player = player_names[current_player_idx]
            player_data = gm.players[current_player]
            player_chips = player_data.get('chips', 0)
            
            # Initialize inventory if not present
            if 'inventory' not in player_data or player_data['inventory'] is None:
                from items import Inventory
                player_data['inventory'] = Inventory()
            
            shop_menu = ShopMenu(screen, player_chips, game_settings)
            available_items = list(registry.items.values())
            if available_items:
                shop_menu.selected_item = available_items[0]
            
            shop_running = True
            while shop_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            shop_running = False
                            # Check window shopper achievement on exit
                            try:
                                from achievements import achievements as achievements_manager
                                visits = player_data.get('shop_visits_no_buy', 0)
                                if visits >= 10:
                                    achievements_manager.unlock('window_shopper')
                            except Exception:
                                pass
                        elif event.key == pygame.K_RETURN and shop_menu.selected_item:
                            # Confirm purchase
                            from ui.ui_utils import show_confirmation_dialog
                            item = shop_menu.selected_item
                            confirm_msg = f"Buy {item.name} for {item.cost} chips? (This adds to your total)"
                            if show_confirmation_dialog(screen, confirm_msg, "Confirm Purchase"):
                                # Try to buy the item (adds chips since goal is to reach 0)
                                player_data['chips'] += item.cost  # ADD chips (penalty for buying)
                                player_data['inventory'].add_item(item)
                                shop_menu.player_chips = player_data['chips']
                                shop_menu.message = f"Bought {item.name}!"
                                shop_menu.message_color = shop_menu.success_color
                                shop_menu.message_timer = pygame.time.get_ticks() + 2000
                                # Play purchase sound
                                try:
                                    audio.play_sound_effect('mouse-click-290204.mp3', volume=0.7)
                                except Exception:
                                    pass
                                
                                # Track purchases for achievements
                                try:
                                    from achievements import achievements as achievements_manager
                                    pc = player_data.get('purchase_count', 0) + 1
                                    player_data['purchase_count'] = pc
                                    
                                    # Track total chips spent
                                    player_data['chips_spent'] = player_data.get('chips_spent', 0) + item.cost
                                    
                                    # Track total items bought
                                    player_data['items_bought'] = player_data.get('items_bought', 0) + 1
                                    
                                    # Check shop achievements
                                    if pc >= 25:
                                        achievements_manager.unlock('shopaholic')
                                    elif pc >= 10:
                                        achievements_manager.unlock('collector')
                                    
                                    if player_data['chips_spent'] >= 100:
                                        achievements_manager.unlock('big_spender')
                                    
                                    # Check for item hoarder (20 total items bought)
                                    if player_data['items_bought'] >= 20:
                                        achievements_manager.unlock('item_hoarder')
                                    
                                    # Reset window shopper counter on purchase
                                    player_data['shop_visits_no_buy'] = 0
                                except Exception:
                                    pass
                            else:
                                # Cancelled purchase - track for window shopper
                                try:
                                    player_data['shop_visits_no_buy'] = player_data.get('shop_visits_no_buy', 0) + 1
                                except Exception:
                                    pass
                        elif event.key == pygame.K_UP:
                            if available_items and shop_menu.selected_item:
                                idx = available_items.index(shop_menu.selected_item)
                                if idx > 0:
                                    shop_menu.selected_item = available_items[idx - 1]
                                    if idx - 1 < shop_menu.scroll_offset:
                                        shop_menu.scroll_offset = idx - 1
                                    # Navigation sound
                                    try:
                                        audio.play_sound_effect('mouse-click-290204.mp3', volume=0.3)
                                    except Exception:
                                        pass
                            elif available_items:
                                shop_menu.selected_item = available_items[0]
                        elif event.key == pygame.K_DOWN:
                            if available_items and shop_menu.selected_item:
                                idx = available_items.index(shop_menu.selected_item)
                                if idx < len(available_items) - 1:
                                    shop_menu.selected_item = available_items[idx + 1]
                                    # Navigation sound
                                    try:
                                        audio.play_sound_effect('mouse-click-290204.mp3', volume=0.3)
                                    except Exception:
                                        pass
                                    if idx + 1 >= shop_menu.scroll_offset + shop_menu.max_items_shown:
                                        shop_menu.scroll_offset = idx + 1 - shop_menu.max_items_shown + 1
                            elif available_items:
                                shop_menu.selected_item = available_items[0]
                
                screen.fill((20, 20, 30))
                shop_menu.draw(available_items)
                # draw any queued achievement popups (non-blocking)
                try:
                    notifier.update()
                    notifier.draw(screen)
                except Exception:
                    pass
                pygame.display.flip()
                clock.tick(60)
            
            show_shop = False

        # Draw the game state with felt texture + vignette (cached)
        # Apply theme colors (high-contrast overrides theme)
        if high_contrast_mode:
            felt_color = (0, 0, 0)
        else:
            felt_color = theme_manager.get_color('background', (12, 80, 34))
        screen.fill(felt_color)
        
        # Diagonal texture overlay (cached)
        if cached_felt_texture is None or cached_felt_texture.get_size() != screen.get_size():
            tex_surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            step = 14
            for x in range(-screen.get_height(), screen.get_width(), step):
                pygame.draw.line(tex_surf, (0, 0, 0, 18), (x, 0), (x + screen.get_height(), screen.get_height()), 1)
            cached_felt_texture = tex_surf
        screen.blit(cached_felt_texture, (0, 0))
        
        # Vignette (cached)
        if cached_vignette is None or cached_vignette.get_size() != screen.get_size():
            cached_vignette = _make_vignette(screen.get_width(), screen.get_height(), max_alpha=140)
        screen.blit(cached_vignette, (0, 0))
        
        current_player = player_names[current_player_idx]
        header_text = (
            f'Current Player: {current_player} | Space: Roll | I: Inventory | S: Shop '
            f'| L: Replays | Tab: Stats | M: Theme | O: Settings | H: Contrast | D: Dyslexia'
        )
        header_color = (0, 0, 0) if high_contrast_mode else (255, 255, 255)
        
        # Header font with dyslexia support
        header_font_key = ('header', font_size, dyslexia_font_mode)
        if header_font_key not in cached_fonts:
            font_family = 'Comic Sans MS' if dyslexia_font_mode else 'Arial'
            cached_fonts[header_font_key] = pygame.font.SysFont(font_family, font_size)
        header_font = cached_fonts[header_font_key]
        
        header = header_font.render(header_text, True, header_color)
        screen.blit(header, (20, 20))

        # Isaiah NPC (left side) -- do not draw in main gameplay
        # (removed from gameplay screen)
        
        # Show tooltip on hover over header
        mx, my = pygame.mouse.get_pos()
        if my < 40:
            from ui.ui_utils import show_tooltip
            tooltip_text = (
                "Space: Roll dice | I: Inventory | S: Shop | L: Replays | Tab: Stats | "
                "M: Theme | O: Settings | H: Contrast | D: Dyslexia | Esc: Return"
            )
            show_tooltip(screen, tooltip_text, mx, my + 20)

        # show transient round message (winner) if present
        if round_message and time.time() < round_message_end:
            rm_font = pygame.font.SysFont('Arial', 28, bold=True)
            rm_surf = rm_font.render(round_message, True, (255, 220, 80))
            rmr = rm_surf.get_rect(center=(screen.get_width() // 2, 60))
            screen.blit(rm_surf, rmr)
        else:
            round_message = None

        # Render players and chips in card-style panels
        y = scale_ui(80)
        die_size = scale_ui(36)
        spacing_x = scale_ui(10)
        chip_radius = scale_ui(8)
        from cards.chips import draw_chip_stack

        panel_padding = scale_ui(12)
        panel_margin = scale_ui(8)
        card_width = screen.get_width() - scale_ui(40)
        
        for i, name in enumerate(gm.player_order):
            chips = gm.players.get(name, {}).get('chips', 0)
            is_current = (i == current_player_idx)
            
            # Calculate card height based on content (responsive)
            result = gm.round_results.get(name)
            has_dice = result is not None
            card_height = scale_ui(70) if has_dice else scale_ui(50)
            
            # Draw card background with gold rim
            card_rect = pygame.Rect(20, y - panel_padding, card_width, card_height)
            
            # Shadow
            shadow_rect = card_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect(), border_radius=10)
            screen.blit(shadow_surf, shadow_rect)
            
            # Card base (darker for current player)
            if high_contrast_mode:
                card_color = (255, 255, 255) if is_current else (220, 220, 220)
                rim_color = (0, 0, 0)
            else:
                card_color = theme_manager.get_color('card_base_current' if is_current else 'card_base', (35, 40, 50))
                rim_color = theme_manager.get_color('card_rim_current' if is_current else 'card_rim', (180, 150, 60))
            pygame.draw.rect(screen, card_color, card_rect, border_radius=10)
            pygame.draw.rect(screen, rim_color, card_rect, 2, border_radius=10)
            
            # Inner highlight at top
            highlight_rect = pygame.Rect(card_rect.x + 2, card_rect.y + 2, card_rect.width - 4, card_height // 3)
            highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surf, (255, 255, 255, 12), highlight_surf.get_rect(), border_radius=8)
            screen.blit(highlight_surf, highlight_rect)
            
            # Content layout (left to right: chips, name, effects, dice)
            content_x = card_rect.x + panel_padding
            content_y = card_rect.y + panel_padding + 4
            
            # draw chip stack (returns rect + metadata)
            stack_rect, chip_metadata = draw_chip_stack(screen, content_x, content_y, chips, chip_radius=chip_radius, max_display=10, font=get_font(scale_ui(14)), time_ms=pygame.time.get_ticks())
            
            # Hover tooltip for chip stack using metadata
            if stack_rect.collidepoint(mx, my):
                # Use metadata directly instead of recalculating
                denom_map = chip_metadata['denominations']
                
                # Build tooltip text
                tooltip_lines = [f"Total: {chip_metadata['total']} chips", ""]
                for d in sorted(denom_map.keys(), reverse=True):
                    cnt = denom_map[d]
                    if cnt > 0:
                        tooltip_lines.append(f"{cnt}x {d} chips")
                if chip_metadata['overflow'] > 0:
                    tooltip_lines.append(f"(+{chip_metadata['overflow']} not shown)")
                
                # Draw tooltip
                tooltip_font_key = ('tooltip', scale_ui(14))
                if tooltip_font_key not in cached_fonts:
                    cached_fonts[tooltip_font_key] = pygame.font.SysFont('Arial', scale_ui(14))
                tooltip_font = cached_fonts[tooltip_font_key]
                tooltip_bg = (40, 40, 50, 230)
                tooltip_border = (220, 185, 75)
                padding = scale_ui(8)
                
                # Calculate tooltip size
                line_surfs = [tooltip_font.render(line, True, (255, 255, 255)) for line in tooltip_lines]
                tooltip_width = max(s.get_width() for s in line_surfs) + padding * 2
                tooltip_height = sum(s.get_height() for s in line_surfs) + padding * 2 + scale_ui(2) * (len(line_surfs) - 1)
                
                # Position tooltip near cursor
                tooltip_x = min(mx + scale_ui(15), screen.get_width() - tooltip_width - 10)
                tooltip_y = min(my + scale_ui(15), screen.get_height() - tooltip_height - 10)
                
                # Draw tooltip background
                tooltip_surf = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
                pygame.draw.rect(tooltip_surf, tooltip_bg, tooltip_surf.get_rect(), border_radius=scale_ui(6))
                pygame.draw.rect(tooltip_surf, tooltip_border, tooltip_surf.get_rect(), 2, border_radius=scale_ui(6))
                screen.blit(tooltip_surf, (tooltip_x, tooltip_y))
                
                # Draw tooltip text
                text_y = tooltip_y + padding
                for surf in line_surfs:
                    screen.blit(surf, (tooltip_x + padding, text_y))
                    text_y += surf.get_height() + scale_ui(2)
            
            # Player name and chip count
            name_x = stack_rect.right + scale_ui(12)
            if high_contrast_mode:
                color = (0, 0, 0) if is_current else (40, 40, 40)
            else:
                color = theme_manager.get_color('text_highlight' if is_current else 'text_secondary', (230, 230, 230))
            # Cache fonts (with dyslexia mode support)
            font_family = 'Comic Sans MS' if dyslexia_font_mode else 'Arial'
            name_font_key = (scale_ui(22), is_current, dyslexia_font_mode)
            if name_font_key not in cached_fonts:
                cached_fonts[name_font_key] = pygame.font.SysFont(font_family, scale_ui(22), bold=is_current)
            name_font = cached_fonts[name_font_key]
            name_txt = name_font.render(name, True, color)
            screen.blit(name_txt, (name_x, content_y - 2))
            
            chip_color = (0, 0, 0) if high_contrast_mode else (200, 200, 200)
            chip_txt = get_font(scale_ui(16)).render(f'{chips} chips', True, chip_color)
            screen.blit(chip_txt, (name_x, content_y + scale_ui(20)))
            
            # Draw active effects
            active_effects = gm.get_active_effects(name)
            if active_effects:
                effects_x = name_x + scale_ui(180)
                status_display.draw_player_effects(screen, name, active_effects, effects_x, content_y - 2, compact=True)

            # Render final roll if available
            if result:
                final = result.get('final_roll', [])
                dice_x = card_rect.right - (len(final) * (die_size + spacing_x)) - panel_padding
                dice_y = content_y
                
                # Animate dice if active
                if roll_anim_active:
                    elapsed = pygame.time.get_ticks() - roll_anim_start_ms
                    progress = min(1.0, elapsed / roll_anim_total_ms)
                    from_faces = roll_anim_from.get(name, final)
                    for j, to_val in enumerate(final):
                        x = dice_x + j * (die_size + spacing_x)
                        # per-die stagger for nicer feel
                        stagger = j * 0.08
                        p = max(0.0, min(1.0, (progress - stagger) / (1.0 - stagger)))
                        draw_die_flipping(screen, x, dice_y, die_size, from_faces[j] if j < len(from_faces) else to_val, to_val, p, particles=dice_particles)
                    if progress >= 1.0:
                        roll_anim_active = False
                        # Play completion tick
                        try:
                            audio.play_sound_effect('mouse-click-290204.mp3', volume=0.5)
                        except Exception:
                            pass
                else:
                    for j, v in enumerate(final):
                        x = dice_x + j * (die_size + spacing_x)
                        draw_die(screen, x, dice_y, die_size, v)
                
                # render the computed hand name/score (below name)
                score_info = GameManager._calculate_score(final)
                try:
                    score_color = (0, 0, 0) if high_contrast_mode else (220, 200, 100)
                    score_txt = get_font(scale_ui(14)).render(score_info.get('name', ''), True, score_color)
                    screen.blit(score_txt, (name_x, content_y + scale_ui(38)))
                except Exception:
                    pass
  
            y += card_height + panel_margin

        # No rolling animation: improvements to die visuals are shown directly
        
        # Draw inventory quick bar at bottom
        current_player = player_names[current_player_idx]
        player_data = gm.players[current_player]
        if 'inventory' in player_data and player_data['inventory']:
            items_list = list(player_data['inventory'].get_all_items().items())[:5]
            if items_list:
                bar_height = scale_ui(60)
                bar_y = screen.get_height() - bar_height - scale_ui(10)
                bar_x = scale_ui(10)
                slot_width = scale_ui(90)
                slot_spacing = scale_ui(8)
                
                for idx, (item_name, qty) in enumerate(items_list):
                    slot_x = bar_x + idx * (slot_width + slot_spacing)
                    slot_rect = pygame.Rect(slot_x, bar_y, slot_width, bar_height)
                    
                    # Slot background
                    slot_surf = pygame.Surface((slot_width, bar_height), pygame.SRCALPHA)
                    if high_contrast_mode:
                        bg_color = (255, 255, 255, 240)
                        border_color = (0, 0, 0)
                    else:
                        bg_color = (35, 40, 50, 220)
                        border_color = (180, 150, 60)
                    pygame.draw.rect(slot_surf, bg_color, slot_surf.get_rect(), border_radius=scale_ui(8))
                    pygame.draw.rect(slot_surf, border_color, slot_surf.get_rect(), 2, border_radius=scale_ui(8))
                    screen.blit(slot_surf, slot_rect)
                    
                    # Item name (shortened)
                    font_family = 'Comic Sans MS' if dyslexia_font_mode else 'Arial'
                    item_font_key = ('item', scale_ui(12), dyslexia_font_mode)
                    if item_font_key not in cached_fonts:
                        cached_fonts[item_font_key] = pygame.font.SysFont(font_family, scale_ui(12), bold=True)
                    item_font = cached_fonts[item_font_key]
                    short_name = item_name[:10] + '..' if len(item_name) > 10 else item_name
                    text_color = (0, 0, 0) if high_contrast_mode else (230, 230, 230)
                    name_surf = item_font.render(short_name, True, text_color)
                    name_rect = name_surf.get_rect(centerx=slot_rect.centerx, top=slot_rect.top + scale_ui(6))
                    screen.blit(name_surf, name_rect)
                    
                    # Quantity
                    qty_color = (40, 40, 40) if high_contrast_mode else (200, 200, 200)
                    qty_surf = item_font.render(f'x{qty}', True, qty_color)
                    qty_rect = qty_surf.get_rect(centerx=slot_rect.centerx, top=name_rect.bottom + scale_ui(2))
                    screen.blit(qty_surf, qty_rect)
                    
                    # Key number
                    key_font_key = ('key', scale_ui(16), dyslexia_font_mode)
                    if key_font_key not in cached_fonts:
                        cached_fonts[key_font_key] = pygame.font.SysFont(font_family, scale_ui(16), bold=True)
                    key_font = cached_fonts[key_font_key]
                    key_color = (0, 0, 0) if high_contrast_mode else (220, 185, 75)
                    key_surf = key_font.render(str(idx + 1), True, key_color)
                    key_rect = key_surf.get_rect(centerx=slot_rect.centerx, bottom=slot_rect.bottom - scale_ui(4))
                    screen.blit(key_surf, key_rect)
                    
                    # Hover highlight
                    if slot_rect.collidepoint(mx, my):
                        highlight_surf = pygame.Surface((slot_width, bar_height), pygame.SRCALPHA)
                        pygame.draw.rect(highlight_surf, (255, 255, 255, 30), highlight_surf.get_rect(), border_radius=scale_ui(8))
                        screen.blit(highlight_surf, slot_rect)

        # Settings overlay (press O)
        if show_settings_overlay:
            overlay_w = scale_ui(380)
            overlay_h = scale_ui(340)
            overlay_x = (screen.get_width() - overlay_w) // 2
            overlay_y = (screen.get_height() - overlay_h) // 2
            overlay_rect = pygame.Rect(overlay_x, overlay_y, overlay_w, overlay_h)
            
            # Semi-transparent background
            overlay_surf = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
            pygame.draw.rect(overlay_surf, (25, 30, 40, 240), overlay_surf.get_rect(), border_radius=scale_ui(12))
            pygame.draw.rect(overlay_surf, (220, 185, 75), overlay_surf.get_rect(), 3, border_radius=scale_ui(12))
            screen.blit(overlay_surf, overlay_rect)
            
            # Title
            font_family = 'Comic Sans MS' if dyslexia_font_mode else 'Arial'
            title_font_key = ('settings_title', scale_ui(24), dyslexia_font_mode)
            if title_font_key not in cached_fonts:
                cached_fonts[title_font_key] = pygame.font.SysFont(font_family, scale_ui(24), bold=True)
            title_font = cached_fonts[title_font_key]
            title_surf = title_font.render('Quick Settings', True, (255, 255, 255))
            title_rect = title_surf.get_rect(centerx=overlay_rect.centerx, top=overlay_rect.top + scale_ui(15))
            screen.blit(title_surf, title_rect)
            
            # Labels and values
            label_font_key = ('settings_label', scale_ui(16), dyslexia_font_mode)
            if label_font_key not in cached_fonts:
                cached_fonts[label_font_key] = pygame.font.SysFont(font_family, scale_ui(16))
            label_font = cached_fonts[label_font_key]
            
            y_pos = overlay_rect.top + scale_ui(60)
            
            # Music volume
            music_vol = audio.get_music_volume() if hasattr(audio, 'get_music_volume') else 0.6
            music_label = label_font.render(f'Music: {int(music_vol * 100)}%', True, (230, 230, 230))
            screen.blit(music_label, (overlay_rect.x + scale_ui(20), y_pos))
            
            # SFX volume
            y_pos += scale_ui(50)
            sfx_vol = audio.sfx_volume if hasattr(audio, 'sfx_volume') else 1.0
            sfx_label = label_font.render(f'SFX: {int(sfx_vol * 100)}%', True, (230, 230, 230))
            screen.blit(sfx_label, (overlay_rect.x + scale_ui(20), y_pos))
            
            # Animation toggle
            y_pos += scale_ui(50)
            anim_status = 'ON' if roll_anim_total_ms > 0 else 'OFF'
            anim_label = label_font.render(f'Animations: {anim_status}', True, (230, 230, 230))
            screen.blit(anim_label, (overlay_rect.x + scale_ui(20), y_pos))
            
            # High contrast mode
            y_pos += scale_ui(40)
            contrast_status = 'ON' if high_contrast_mode else 'OFF'
            contrast_color = (0, 255, 0) if high_contrast_mode else (230, 230, 230)
            contrast_label = label_font.render(f'High Contrast (H): {contrast_status}', True, contrast_color)
            screen.blit(contrast_label, (overlay_rect.x + scale_ui(20), y_pos))
            
            # Dyslexia font mode
            y_pos += scale_ui(40)
            dyslexia_status = 'ON' if dyslexia_font_mode else 'OFF'
            dyslexia_color = (0, 255, 0) if dyslexia_font_mode else (230, 230, 230)
            dyslexia_label = label_font.render(f'Dyslexia Font (D): {dyslexia_status}', True, dyslexia_color)
            screen.blit(dyslexia_label, (overlay_rect.x + scale_ui(20), y_pos))
            
            # Instructions
            y_pos += scale_ui(40)
            inst_font_key = ('settings_inst', scale_ui(12), dyslexia_font_mode)
            if inst_font_key not in cached_fonts:
                font_family = 'Comic Sans MS' if dyslexia_font_mode else 'Arial'
                cached_fonts[inst_font_key] = pygame.font.SysFont(font_family, scale_ui(12))
            inst_font = cached_fonts[inst_font_key]
            inst_text = 'Press O to close | Use main Settings menu for full control'
            inst_surf = inst_font.render(inst_text, True, (180, 180, 180))
            inst_rect = inst_surf.get_rect(centerx=overlay_rect.centerx, top=y_pos)
            screen.blit(inst_surf, inst_rect)
        
        # Update and draw dice particles
        dt = clock.get_time() / 1000.0  # Convert to seconds
        dice_particles[:] = [p for p in dice_particles if p.update(dt)]
        for particle in dice_particles:
            particle.draw(screen)
        
        # draw any queued achievement popups (non-blocking)
        try:
            notifier.update()
            notifier.draw(screen)
        except Exception:
            pass

        # Draw overlays after flip content but before next frame
        if show_stats_overlay:
            try:
                # Semi-transparent overlay
                overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                screen.blit(overlay, (0, 0))
                # Render summary
                summary = stats_tracker.get_summary()
                title_font = get_font(scale_ui(22), bold=True)
                body_font = get_font(scale_ui(16))
                title = title_font.render('Statistics Summary', True, theme_manager.get_color('text_primary'))
                screen.blit(title, (scale_ui(40), scale_ui(60)))
                lines = [
                    f"Total Games: {summary['total_games']}",
                    f"Total Rounds: {summary['total_rounds']}",
                    f"Total Playtime: {int(summary['total_playtime'])}s",
                ]
                y = scale_ui(110)
                for line in lines:
                    surf = body_font.render(line, True, theme_manager.get_color('text_secondary'))
                    screen.blit(surf, (scale_ui(40), y))
                    y += scale_ui(28)
            except Exception:
                pass

        if show_theme_menu:
            try:
                overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                menu_w = scale_ui(520)
                menu_h = scale_ui(360)
                menu_x = (screen.get_width() - menu_w)//2
                menu_y = (screen.get_height() - menu_h)//2
                menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
                pygame.draw.rect(screen, theme_manager.get_color('card_base'), menu_rect, border_radius=scale_ui(8))
                pygame.draw.rect(screen, theme_manager.get_color('card_rim'), menu_rect, 2, border_radius=scale_ui(8))
                title_font = get_font(scale_ui(20), bold=True)
                title = title_font.render('Theme Selector (press number to apply)', True, theme_manager.get_color('text_primary'))
                screen.blit(title, (menu_x + scale_ui(20), menu_y + scale_ui(16)))
                y = menu_y + scale_ui(56)
                idx = 1
                for key, name in theme_manager.list_themes():
                    line = f"{idx}. {name}  ({key})"
                    surf = get_font(scale_ui(16)).render(line, True, theme_manager.get_color('text_secondary'))
                    screen.blit(surf, (menu_x + scale_ui(24), y))
                    y += scale_ui(30)
                    idx += 1
            except Exception:
                pass

        if show_replay_browser:
            try:
                overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                screen.blit(overlay, (0, 0))
                menu_w = scale_ui(640)
                menu_h = scale_ui(420)
                menu_x = (screen.get_width() - menu_w)//2
                menu_y = (screen.get_height() - menu_h)//2
                menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
                pygame.draw.rect(screen, theme_manager.get_color('card_base'), menu_rect, border_radius=scale_ui(8))
                pygame.draw.rect(screen, theme_manager.get_color('card_rim'), menu_rect, 2, border_radius=scale_ui(8))
                title = get_font(scale_ui(20), bold=True).render('Replays', True, theme_manager.get_color('text_primary'))
                screen.blit(title, (menu_x + scale_ui(18), menu_y + scale_ui(12)))
                # List replays
                replays = replay_system.list_replays()
                y = menu_y + scale_ui(50)
                idx = 1
                for r in replays[:12]:
                    info = f"{idx}. {r.get('filename')} - rounds: {r.get('rounds')} winner: {r.get('winner')}"
                    surf = get_font(scale_ui(14)).render(info, True, theme_manager.get_color('text_secondary'))
                    screen.blit(surf, (menu_x + scale_ui(18), y))
                    y += scale_ui(28)
                    idx += 1
                if not replays:
                    surf = get_font(scale_ui(14)).render('No replays found.', True, theme_manager.get_color('text_secondary'))
                    screen.blit(surf, (menu_x + scale_ui(18), y))
                # If a replay is loaded and playback is active, advance events by timer
                if replay_playing and not replay_paused and replay_system.playback_data is not None:
                    replay_playback_timer += dt
                    events = replay_system.playback_data.get('events', [])
                    # Dispatch events whose timestamp <= timer
                    while replay_playback_index < len(events) and events[replay_playback_index]['timestamp'] <= replay_playback_timer:
                        ev = replay_system.get_next_event()
                        if ev:
                            notifier.show('Replay Event', f"{ev.get('type')}: {str(ev.get('data'))[:120]}")
                        replay_playback_index += 1
                # Show loaded replay status
                status_y = menu_y + menu_h - scale_ui(48)
                if current_replay_info:
                    st = get_font(scale_ui(14)).render(f"Loaded: {current_replay_info.get('filename')} | Play: Space | Step: → | Close: Esc", True, theme_manager.get_color('text_secondary'))
                    screen.blit(st, (menu_x + scale_ui(18), status_y))
            except Exception:
                pass
        # After drawing overlays, flip to show them
        try:
            pygame.display.flip()
        except Exception:
            pass

def main():
    pygame.init()
    pygame.font.init()

    WINDOW_WIDTH, WINDOW_HEIGHT = 900, 600
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Game - Launcher")

    # Show the intro/splash screen before the main menu
    try:
        from ui.intro_screen import IntroScreen
        intro = IntroScreen(
                title='Zanzibar',
                subtitle='A Dice Game by I paid $1,152.60 to have this team name',
                duration=5.0,
                use_roulette_table=True,
                use_blank_background=False
            )
        intro.run(screen)
    except Exception:
        # If intro fails for any reason, continue to the menu
        pass

    menu = StartMenu(screen, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    # load settings and initialize audio
    settings = load_settings()
    game_settings = Settings()  # Initialize game settings (keybindings, etc.)
    audio = AudioManager(audio_folder=ASSETS_DIR)
    try:
        audio.set_sfx_volume(settings.get('sfx_volume', 1.0))
    except Exception:
        pass
    music_file = settings.get('music_file', 'test.mp3')
    music_vol = settings.get('music_volume', 0.6)
    audio.play_music(music_file, loop=True, volume=music_vol)

    while True:
        choice = menu.run()
        if choice == 'play':
            # Launch the full Zanzibar-style dice game engine (with pre-game setup)
            run_game_engine(screen, audio)
            continue
        elif choice == 'change_song':
            changer = ChangeSongMenu(screen, audio_folder=os.path.join(ASSETS_DIR, 'songs'), audio_manager=audio)
            sel = changer.run()
            if sel:
                s = load_settings()
                s['music_file'] = sel
                save_settings(s)
                audio.change_music(sel, loop=True)
            continue
        elif choice == 'settings':
            settings_menu = AudioSettingsMenu(screen, audio_manager=audio)
            result = settings_menu.run()
            if isinstance(result, dict):
                s = load_settings()
                s['music_volume'] = result.get('music_volume', s.get('music_volume', 0.6))
                s['sfx_volume'] = result.get('sfx_volume', s.get('sfx_volume', 1.0))
                save_settings(s)
                try:
                    audio.set_sfx_volume(s.get('sfx_volume', 1.0))
                    audio.set_music_volume(s.get('music_volume', 0.6))
                except Exception:
                    pass
            continue
        elif choice == 'keybindings':
            # Show keybindings menu
            keybindings_menu = KeybindingsMenu(screen, game_settings)
            clock = pygame.time.Clock()
            kb_running = True
            while kb_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if keybindings_menu.handle_event(event):
                        kb_running = False
                
                # Clear screen with a solid background
                screen.fill((15, 15, 20))
                keybindings_menu.draw()
                pygame.display.flip()
                clock.tick(60)
            continue
        elif choice == 'achievements':
            ach_menu = AchievementsMenu(screen)
            clock = pygame.time.Clock()
            ach_running = True
            while ach_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if ach_menu.handle_event(event):
                        ach_running = False

                # Clear screen with a solid background
                screen.fill((15, 15, 20))
                ach_menu.draw()
                pygame.display.flip()
                clock.tick(60)
            continue
        elif choice == 'quit':
            break

    # cleanup
    try:
        audio.stop_music()
    except Exception:
        pass
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
