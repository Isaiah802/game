"""Simple audio smoke test for the project's AudioManager."""

import time
import os
from uno_game.audio.audio import AudioManager


def main():
    # Initialize AudioManager (will search for assets/songs and assets/sfx)
    audio = AudioManager(audio_folder=None)

    if not audio.available:
        print("[Test] Audio system not available. Skipping test.")
        return

    # --- Test background music ---
    music_file = "test.mp3"
    music_path = os.path.join(audio.songs_folder, music_file)
    if os.path.exists(music_path):
        print(f"[Test] Playing music: {music_file}")
        audio.play_music(music_file, loop=False, volume=0.7)
        time.sleep(5)
        audio.stop_music()
    else:
        print(f"[Test] Skipping music test, file not found: {music_path}")

    # --- Test sound effect ---
    sfx_file = "cubes.mp3"  # make sure this exists in assets/sfx
    sfx_path = os.path.join(audio.sfx_folder, sfx_file)
    if os.path.exists(sfx_path):
        print(f"[Test] Playing sound effect: {sfx_file}")
        audio.play_sound_effect(sfx_file, volume=0.8)
        time.sleep(2)
    else:
        print(f"[Test] Skipping SFX test, file not found: {sfx_path}")


if __name__ == "__main__":
    main()
