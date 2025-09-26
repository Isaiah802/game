import os
import sys
import time
import pygame
from audio.audio import AudioManager
from cards.card import create_uno_deck, draw_uno_card_pygame

# Alias the pygame draw helper to the short name used in the main loop
draw_uno_card = draw_uno_card_pygame
import random
import json

from ui.change_song_menu import ChangeSongMenu
from ui.audio_settings import AudioSettingsMenu

# ---------------- Paths ----------------
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
CARDS_DIR = os.path.join(ASSETS_DIR, 'cards')
AUDIO_SONGS_DIR = os.path.join(ASSETS_DIR, 'songs')
AUDIO_SFX_DIR = os.path.join(ASSETS_DIR, 'sfx')
AUDIO_ASSETS_BASE = ASSETS_DIR

# Simple settings persistence
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

# ---------------- Initialize Pygame ----------------
pygame.init()
pygame.font.init()


# ---------------- Load a Sample Card Image ----------------
# We'll render UNO cards directly in pygame (ported from cards/card.py)





# Prepare a shuffled deck and select 10 cards to display
full_deck = create_uno_deck()
random.shuffle(full_deck)
display_cards = [full_deck.pop() for _ in range(min(10, len(full_deck)))]

# ---------------- Create Window ----------------
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Uno Game Prototype")

# Import the menu
from ui.start_menu import StartMenu

# ---------------- Simple Game Loop ----------------
def main_loop():
    print("\n=== Welcome to Uno Game Prototype ===")
    print("Press Ctrl+C to quit\n")
    
    turn = 0
    clock = pygame.time.Clock()
    # Initialize audio manager here so it doesn't run on import
    # Load settings and initialize audio with persisted preferences
    settings = load_settings()
    # Initialize AudioManager with assets base; it will resolve songs/ and sfx/
    audio = AudioManager(audio_folder=AUDIO_ASSETS_BASE)
    try:
        audio.set_sfx_volume(settings.get('sfx_volume', 1.0))
    except Exception:
        pass
    music_file = settings.get('music_file', 'test.mp3')
    music_vol = settings.get('music_volume', 0.6)
    # Start background music (looping). If it fails, the AudioManager will
    # print an error and the game continues without sound.
    audio.play_music(music_file, loop=True, volume=music_vol)

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Clear screen
            screen.fill((0, 128, 0))  # Green background
            
            # Draw card if loaded
            # Draw 10 cards in two rows (ported from turtle implementation)
            card_spacing_x = 95
            card_spacing_y = 140
            start_x_top_row = (WINDOW_WIDTH - (5 * 80 + 4 * (card_spacing_x - 80))) // 2
            start_y_top_row = 100
            start_x_bottom_row = start_x_top_row
            start_y_bottom_row = 260

            for i, card in enumerate(display_cards):
                if i < 5:
                    cx = start_x_top_row + (i * card_spacing_x)
                    cy = start_y_top_row
                else:
                    cx = start_x_bottom_row + ((i - 5) * card_spacing_x)
                    cy = start_y_bottom_row
                draw_uno_card(screen, cx, cy, card)
            
            pygame.display.flip()
            
            # Print turn info to console
            print(f"Turn {turn + 1}: Player {turn % 2 + 1}'s move")
            time.sleep(2)  # Simulate turn delay
            turn += 1
            
            clock.tick(60)  # Limit to 60 FPS
            
    except KeyboardInterrupt:
        print("\n[Game] Exiting...")
    finally:
        # Stop music if audio manager was created
        try:
            audio.stop_music()
        except Exception:
            pass
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Keep returning to the Start Menu until the user quits.
    menu = StartMenu(screen, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    while True:
        choice = menu.run()
        if choice == 'play':
            # start the game; when main_loop returns we'll show the menu again
            main_loop()
        elif choice == 'change_song':
            # Launch an interactive change-song UI with live preview, persist selection
            audio = AudioManager(audio_folder=AUDIO_ASSETS_BASE)
            changer = ChangeSongMenu(screen, audio_folder=AUDIO_SONGS_DIR, audio_manager=audio)
            sel = changer.run()
            if sel:
                s = load_settings()
                s['music_file'] = sel
                save_settings(s)
                audio.change_music(sel, loop=True)
                print(f"Changed song to {sel}")
            # return to start menu (do not auto-start)
            continue
        elif choice == 'settings':
            # Open audio settings menu
            audio = AudioManager(audio_folder=AUDIO_ASSETS_BASE)
            settings_menu = AudioSettingsMenu(screen, audio_manager=audio)
            result = settings_menu.run()
            if isinstance(result, dict):
                s = load_settings()
                s['music_volume'] = result.get('music_volume', s.get('music_volume', 0.6))
                s['sfx_volume'] = result.get('sfx_volume', s.get('sfx_volume', 1.0))
                save_settings(s)
            # return to start menu
            continue
        elif choice == 'quit':
            print("Goodbye")
            break
        else:
            # Unknown result — go back to menu
            continue
