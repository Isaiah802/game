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
from audio.audio import AudioManager
from ui.start_menu import StartMenu
from ui.change_song_menu import ChangeSongMenu
from ui.audio_settings import AudioSettingsMenu
from cards.card import create_dice_rolls


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


def main():
    pygame.init()
    pygame.font.init()

    WINDOW_WIDTH, WINDOW_HEIGHT = 900, 600
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Game - Launcher")

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
            # placeholder for a full game
            print('Play selected (no full game implemented).')
            continue
        elif choice == 'dice':
            run_dice_demo(screen, audio, num_dice=10)
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
