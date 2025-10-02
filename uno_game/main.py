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
from .audio.audio import AudioManager
from .ui.start_menu import StartMenu
from .ui.change_song_menu import ChangeSongMenu
from .ui.audio_settings import AudioSettingsMenu
from .cards.card import create_dice_rolls
from .game.game_engine import GameManager


BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.json')


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


def draw_die(surface: pygame.Surface, x: int, y: int, size: int, value: int):
    # Draw white rectangle with black border
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, (255, 255, 255), rect)
    pygame.draw.rect(surface, (0, 0, 0), rect, 2)

    # pip positions
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


def run_dice_demo(screen: pygame.Surface, audio: AudioManager, num_dice: int = 10):
    clock = pygame.time.Clock()
    running = True
    rolls = create_dice_rolls(num_dice)
    font = pygame.font.SysFont('Arial', 20)

    # try to play a roll sfx when rolling
    sfx_name = 'mouse-click-290204.mp3'  # included asset

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    rolls = create_dice_rolls(num_dice)
                    # play sfx if available
                    try:
                        audio.play_sound_effect(sfx_name, volume=0.8)
                    except Exception:
                        pass
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # draw background
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


def player_setup(screen: pygame.Surface):
    """Pre-game form with clickable buttons, caret blinking, and a scrollable players list.

    Returns (player_names, starting_chips) or None if cancelled.
    """
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 20)
    input_text = ''
    players = []
    starting_chips = 20  # fixed per requirement

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
        col = (200, 200, 200)
        if rect.collidepoint(pygame.mouse.get_pos()):
            col = (170, 170, 170)
        pygame.draw.rect(screen, col, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        txt = font.render(text, True, (0, 0, 0))
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
                        players.append(input_text.strip())
                        input_text = ''
                        error_msg = ''
                elif event.key == pygame.K_BACKSPACE:
                    if input_text:
                        input_text = input_text[:-1]
                    elif players:
                        players.pop()
                elif event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 1)
                elif event.key == pygame.K_DOWN:
                    max_off = max(0, len(players) - 8)
                    scroll_offset = min(max_off, scroll_offset + 1)
                else:
                    ch = event.unicode
                    if ch and ch.isprintable():
                        input_text += ch

        # Handle button clicks
        if mouse_pressed:
            if add_btn.collidepoint((mx, my)):
                if input_text.strip():
                    players.append(input_text.strip())
                    input_text = ''
                    error_msg = ''
            elif remove_btn.collidepoint((mx, my)):
                if players:
                    players.pop()
            elif start_btn.collidepoint((mx, my)):
                if len(players) < 2:
                    error_msg = 'Need at least 2 players'
                else:
                    return players, starting_chips
            elif cancel_btn.collidepoint((mx, my)):
                return None

        # Draw UI
        screen.fill((25, 100, 25))
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

        # Input box
        input_box = pygame.Rect(20, y, 300, 36)
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
        input_surf = font.render(input_text, True, (255, 255, 255))
        screen.blit(input_surf, (input_box.x + 6, input_box.y + 6))
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
        for p in players[start_idx:end_idx]:
            ptxt = font.render('- ' + p, True, (240, 240, 240))
            screen.blit(ptxt, (40, y))
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
        if caret_visible:
            caret_x = input_box.x + 6 + input_surf.get_width()
            caret_y1 = input_box.y + 6
            caret_y2 = input_box.y + input_box.height - 6
            pygame.draw.line(screen, (255, 255, 255), (caret_x, caret_y1), (caret_x, caret_y2), 2)

        # Draw buttons
        draw_button(add_btn, 'Add')
        draw_button(remove_btn, 'Remove')
        draw_button(start_btn, 'Start')
        draw_button(cancel_btn, 'Cancel')

        # Error message
        if error_msg:
            em = font.render(error_msg, True, (255, 100, 100))
            screen.blit(em, (20, 300))

        pygame.display.flip()
        clock.tick(60)


def run_game_engine(screen: pygame.Surface, audio: AudioManager):
    """Runs the Zanzibar GameManager in interactive mode inside the pygame window.

    Controls:
    - Space: Play next round
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
    gm = GameManager(player_names, starting_chips)

    # UI state
    running = True
    orig_size = screen.get_size()
    is_fullscreen = False
    round_message = None
    round_message_end = 0.0
    animating = False
    anim_end = 0.0
    anim_duration = 0.8
    while running:
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
                elif event.key == pygame.K_SPACE:
                    # start dice roll animation; actual round runs after animation
                    if not animating:
                        animating = True
                        anim_end = time.time() + anim_duration
                        # play a roll sfx if available
                        try:
                            audio.play_sound_effect('dice_bounce.mp3', volume=0.8)
                        except Exception:
                            try:
                                audio.play_sound_effect('whoosh.mp3', volume=0.6)
                            except Exception:
                                pass
                    # play a round  
                    gm.play_round(screen)

        # Draw the game state
        screen.fill((40, 40, 60))
        header = font.render('Press Space to play next round, Esc to return to menu', True, (255, 255, 255))
        screen.blit(header, (20, 20))

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
            # draw chip stack at fixed left column, then render player text to the right of chips
            stack_rect = draw_chip_stack(screen, 20, y - 6, chips, chip_radius=8, max_display=10, font=font)
            try:
                txt = font.render(f'{name}: {chips} chips', True, (230, 230, 230))
                screen.blit(txt, (stack_rect.right + 8, y))
            except Exception:
                pass

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

        # If animating, draw rolling dice animation in the center area
        if animating:
            # draw three animated dice near the header
            anim_die_size = 48
            cx = screen.get_width() // 2 - (anim_die_size * 3 + spacing_x * 2) // 2
            for k in range(3):
                face = random.randint(1, 6)
                draw_die(screen, cx + k * (anim_die_size + spacing_x), 100, anim_die_size, face)
            # check animation end
            if time.time() >= anim_end:
                animating = False
                # run actual round now
                gm.play_round()
                # compute winner for display
                scores = {player: GameManager._calculate_score(res.get('final_roll', [])) for player, res in gm.round_results.items()}
                if scores:
                    winner = max(scores, key=lambda p: scores[p]['score'])
                    round_message = f"Round winner: {winner} - {scores[winner]['name']}"
                    round_message_end = time.time() + 3.0

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
        intro = IntroScreen(title='Zanzibar', subtitle='A Dice Game by I paid $1,152.60 to have this team name', duration=5.0)
        intro.run(screen)
    except Exception:
        # If intro fails for any reason, continue to the menu
        pass

    menu = StartMenu(screen, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    # load settings and initialize audio
    settings = load_settings()
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
