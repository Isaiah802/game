import os
import sys
import time
import pygame
from audio.audio import AudioManager
from cards.card import create_uno_deck, draw_uno_card_pygame

# Alias the pygame draw helper to the short name used in the main loop
draw_uno_card = draw_uno_card_pygame
import random

# ---------------- Paths ----------------
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
CARDS_DIR = os.path.join(ASSETS_DIR, 'cards')
AUDIO_DIR = os.path.join(ASSETS_DIR, 'audio')

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

# ---------------- Simple Game Loop ----------------
def main_loop():
    print("\n=== Welcome to Uno Game Prototype ===")
    print("Press Ctrl+C to quit\n")
    
    turn = 0
    clock = pygame.time.Clock()
    # Initialize audio manager here so it doesn't run on import
    audio = AudioManager(audio_folder=os.path.join(ASSETS_DIR, 'sounds'))
    # Start background music (looping). If it fails, the AudioManager will
    # print an error and the game continues without sound.
    audio.play_music('test.mp3', loop=True, volume=0.6)

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
    main_loop()
