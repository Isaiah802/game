"""Simple audio smoke test for the project's AudioManager."""
from audio.audio import AudioManager
import time


def main():
    audio = AudioManager(audio_folder=None)
    audio.play_music("test.mp3", loop=False, volume=0.7)

    print("Playing music for 5 seconds...")
    time.sleep(5)
    audio.stop_music()


if __name__ == "__main__":
    main()
