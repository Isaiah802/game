import os
import sys
import time
import pygame
from audio.audio import AudioManager

# ---------------- Paths ----------------
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
CARDS_DIR = os.path.join(ASSETS_DIR, 'cards')
AUDIO_DIR = os.path.join(ASSETS_DIR, 'audio')

# ---------------- Initialize Pygame ----------------
pygame.init()
pygame.mixer.init()

# ---------------- Initialize Audio ----------------
audio = AudioManager(AUDIO_DIR)
# Only pass the filename, NOT the full path
audio.play_music('uno_game\assets\sound\test.mp3', loop=True, volume=0.6)

# ---------------- Load a Sample Card Image ----------------
sample_card_path = os.path.join(CARDS_DIR, 'funny_card.png')  # Replace with your image
if os.path.exists(sample_card_path):
    card_image = pygame.image.load(sample_card_path)
    print("[Graphics] Loaded sample card image successfully!")
else:
    card_image = None
    print(f"[Graphics] Warning: {sample_card_path} not found!")

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
    
    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Clear screen
            screen.fill((0, 128, 0))  # Green background
            
            # Draw card if loaded
            if card_image:
                screen.blit(card_image, (WINDOW_WIDTH//2 - card_image.get_width()//2,
                                         WINDOW_HEIGHT//2 - card_image.get_height()//2))
            
            pygame.display.flip()
            
            # Print turn info to console
            print(f"Turn {turn + 1}: Player {turn % 2 + 1}'s move")
            time.sleep(2)  # Simulate turn delay
            turn += 1
            
            clock.tick(60)  # Limit to 60 FPS
            
    except KeyboardInterrupt:
        print("\n[Game] Exiting...")
    finally:
        audio.stop_music()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main_loop()
