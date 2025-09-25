# uno_game/tests/test_audio.py
from uno_game.audio.audio import AudioManager
import time

def main():
    audio = AudioManager()
    audio.play_music("test.mp3", loop=False, volume=0.7)

    print("Playing music for 5 seconds...")
    time.sleep(5)
    audio.stop_music()

if __name__ == "__main__":
    main()
