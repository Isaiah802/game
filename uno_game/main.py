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


BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.json')

# Cache for pre-rendered die sprites: {(size, face): Surface}
DIE_SPRITE_CACHE = {}

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
    key = (size, face)
    if key in DIE_SPRITE_CACHE:
        return DIE_SPRITE_CACHE[key]

    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, size, size)
    border_radius = max(4, size // 8)

    # shadow
    shadow = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 48), (size*0.08, size*0.7, size*0.84, size*0.24))
    surf.blit(shadow, (0, 0))

    # base face with subtle bevel (drawn as two layered rects)
    base_col = (245, 245, 245)
    inner_col = (228, 228, 232)
    pygame.draw.rect(surf, base_col, rect, border_radius=border_radius)
    inner = rect.inflate(-size*0.08, -size*0.08)
    pygame.draw.rect(surf, inner_col, inner, border_radius=max(2, border_radius-2))

    # top-left highlight
    hl = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(hl, (255, 255, 255, 36), (0, 0, size, size//2), border_radius=border_radius)
    surf.blit(hl, (0, 0))

    # pip helper with slight rim
    def pip(cx, cy, r):
        # shadow rim
        pygame.draw.circle(surf, (20, 20, 20, 120), (int(cx+1), int(cy+1)), r)
        pygame.draw.circle(surf, (8, 8, 8), (int(cx), int(cy)), r-1)
        # small glossy spot
        if r >= 4:
            pygame.draw.circle(surf, (255, 255, 255, 40), (int(cx - r*0.3), int(cy - r*0.3)), max(1, r//3))

    # pip layout relative to rect
    col_1 = size * 0.22
    col_2 = size * 0.5
    col_3 = size * 0.78
    row_1 = size * 0.22
    row_2 = size * 0.5
    row_3 = size * 0.78
    r = max(2, size // 10)

    if face in (1, 3, 5):
        pip(col_2, row_2, r)
    if face in (2, 3, 4, 5, 6):
        pip(col_1, row_1, r)
        pip(col_3, row_3, r)
    if face in (4, 5, 6):
        pip(col_3, row_1, r)
        pip(col_1, row_3, r)
    if face == 6:
        pip(col_1, row_2, r)
        pip(col_3, row_2, r)

    # subtle border
    pygame.draw.rect(surf, (30, 30, 30), rect, 1, border_radius=border_radius)

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


def draw_die_flipping(surface: pygame.Surface, x: int, y: int, size: int, from_val: int, to_val: int, progress: float):
    """Draw a die flipping from `from_val` to `to_val` where progress is 0..1.

    The flip uses an X-scale shrink to mid-point and swaps face at 0.5.
    """
    # clamp and ease
    p = max(0.0, min(1.0, progress))
    def ease(t):
        return 3*t*t - 2*t*t*t
    pe = ease(p)

    # decide which face to display; swap to target at midpoint for a flip effect
    if pe < 0.5:
        face = from_val if from_val else random.randint(1, 6)
    else:
        face = to_val if to_val else random.randint(1, 6)

    # compute horizontal squash (width scales down toward 0 at mid-flip)
    if pe < 0.5:
        scale_x = 1.0 - (pe / 0.5)
    else:
        scale_x = (pe - 0.5) / 0.5

    w = max(6, int(size * scale_x))
    cx = x + (size - w) // 2

    try:
        # get the face sprite and scale horizontally to simulate flip
        spr = _render_die_sprite(size, face)
        # when squashed to very small width, scale to at least 1 pixel to avoid errors
        scaled = pygame.transform.smoothscale(spr, (max(1, w), size))
        surface.blit(scaled, (cx, y))
        # draw subtle border when visible
        if w > 4:
            pygame.draw.rect(surface, (30, 30, 30), pygame.Rect(cx, y, w, size), 1)
    except Exception:
        # fallback: draw a simple scaled rect
        if w > 2:
            rect = pygame.Rect(cx, y, w, size)
            pygame.draw.rect(surface, (245, 245, 245), rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 1)
        else:
            # tiny mid-flip line to hint at motion
            pygame.draw.line(surface, (0,0,0), (x+size//2, y), (x+size//2, y+size), 2)


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
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 20)

    # For simplicity, player names and starting chips are provided before starting
    # the engine via a small pre-game form.
    setup = player_setup(screen)
    if not setup:
        return
    player_names, starting_chips = setup
    
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
    
    # Track current player (for shop/inventory)
    current_player_idx = 0
    
    # Menu states
    show_inventory = False
    show_shop = False
    
    # Initialize status display
    status_display = StatusDisplay()
    
    while running:
        # frame timing
        ms = clock.tick(60)
        dt = ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
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
                    # Open inventory menu
                    show_inventory = True
                elif event.key == pygame.K_s:
                    # Open shop menu
                    show_shop = True
                elif event.key == pygame.K_TAB:
                    # Switch current player
                    current_player_idx = (current_player_idx + 1) % len(player_names)
                elif event.key == pygame.K_SPACE:
                    # Play a round immediately and show improved (3D) dice.
                    # Play dice roll sound
                    try:
                        audio.play_sound_effect('dice_bounce.mp3', volume=0.6)
                    except Exception:
                        pass
                    try:
                        gm.play_round()
                    except Exception:
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

        # Draw the game state (flat fill)
        screen.fill((40, 40, 60))
        current_player = player_names[current_player_idx]
        header = font.render(f'Current Player: {current_player} | Space: Roll | I: Inventory | S: Shop | Tab: Switch Player | Esc: Menu', True, (255, 255, 255))
        screen.blit(header, (20, 20))
        
        # Show tooltip on hover over header
        mx, my = pygame.mouse.get_pos()
        if my < 40:
            from ui.ui_utils import show_tooltip
            tooltip_text = "Space: Roll dice | I: Open inventory | S: Shop for items | Tab: Switch player view | Esc: Return to menu"
            show_tooltip(screen, tooltip_text, mx, my + 20)

        # show transient round message (winner) if present
        if round_message and time.time() < round_message_end:
            rm_font = pygame.font.SysFont('Arial', 28, bold=True)
            rm_surf = rm_font.render(round_message, True, (255, 220, 80))
            rmr = rm_surf.get_rect(center=(screen.get_width() // 2, 60))
            screen.blit(rm_surf, rmr)
        else:
            round_message = None

        # Render players and chips
        y = 80
        die_size = 36
        spacing_x = 10
        from cards.chips import draw_chip_stack

        for i, name in enumerate(gm.player_order):
            chips = gm.players.get(name, {}).get('chips', 0)
            
            # Highlight current player
            is_current = (i == current_player_idx)
            if is_current:
                highlight_rect = pygame.Rect(10, y - 12, screen.get_width() - 20, 48)
                pygame.draw.rect(screen, (80, 100, 120), highlight_rect, border_radius=8)
                pygame.draw.rect(screen, (150, 180, 200), highlight_rect, 2, border_radius=8)
            
            # draw chip stack at fixed left column, then render player text to the right of chips
            stack_rect = draw_chip_stack(screen, 20, y - 6, chips, chip_radius=8, max_display=10, font=font)
            try:
                color = (255, 255, 120) if is_current else (230, 230, 230)
                txt = font.render(f'{name}: {chips} chips', True, color)
                screen.blit(txt, (stack_rect.right + 8, y))
            except Exception:
                pass

            # Draw active effects for this player
            active_effects = gm.get_active_effects(name)
            if active_effects:
                effects_x = stack_rect.right + 150
                status_display.draw_player_effects(screen, name, active_effects, effects_x, y - 10, compact=True)

            # Render final roll if available
            result = gm.round_results.get(name)
            if result:
                final = result.get('final_roll', [])
                for j, v in enumerate(final):
                    x = 220 + j * (die_size + spacing_x)
                    draw_die(screen, x, y - 6, die_size, v)
                # render the computed hand name/score
                score_info = GameManager._calculate_score(final)
                try:
                    score_txt = font.render(score_info.get('name', ''), True, (200, 200, 120))
                    screen.blit(score_txt, (220, y + 18))
                except Exception:
                    pass
  
            y += 50

        # No rolling animation: improvements to die visuals are shown directly

        # draw any queued achievement popups (non-blocking)
        try:
            notifier.update()
            notifier.draw(screen)
        except Exception:
            pass
        pygame.display.flip()
        clock.tick(60)

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
