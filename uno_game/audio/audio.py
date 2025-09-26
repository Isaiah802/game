# audio/audio.py
import os
import pygame
import sys

# ---------------- Audio Manager ----------------
class AudioManager:
    def __init__(self, audio_folder=None):
        """Initialize the AudioManager.

        If audio_folder is None, try these relative folders under the package's
        assets folder (in order): 'sounds', 'sound', 'audio'. If none exist the
        provided path will still be used, but playback calls will fail gracefully.
        The manager will not call sys.exit on init failure; instead it sets
        self.available to False and playback methods return False.
        """
        base_assets = os.path.join(os.path.dirname(__file__), '..', 'assets')
        if audio_folder is None:
            candidates = [
                os.path.join(base_assets, 'sounds'),
                os.path.join(base_assets, 'sound'),
                os.path.join(base_assets, 'audio'),
            ]
            found = next((p for p in candidates if os.path.exists(p)), None)
            audio_folder = found if found is not None else candidates[-1]

        self.audio_folder = os.path.abspath(audio_folder)

        # Try to initialize pygame mixer. If it fails, mark unavailable but don't exit.
        self.available = True
        try:
            pygame.init()
            pygame.mixer.init()
        except Exception as e:
            print(f"[AudioManager] Pygame mixer init failed: {e}")
            self.available = False

    def play_music(self, filename, loop=True, volume=0.5):
        """Play background music indefinitely or once"""
        if not self.available:
            print("[AudioManager] Cannot play music: mixer not available")
            return False
        music_path = os.path.join(self.audio_folder, filename)
        if not os.path.exists(music_path):
            print(f"[AudioManager] Error: File not found: {music_path}")
            return False

        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(volume)
        loops = -1 if loop else 0
        pygame.mixer.music.play(loops)
        print(f"[AudioManager] Playing music: {filename}")
        return True

    def stop_music(self):
        """Stop background music"""
        if not self.available:
            return
        pygame.mixer.music.stop()
        print("[AudioManager] Music stopped")

    def play_sound(self, filename, volume=0.5):
        """Play a short sound effect"""
        if not self.available:
            print("[AudioManager] Cannot play sound: mixer not available")
            return False
        sound_path = os.path.join(self.audio_folder, filename)
        if not os.path.exists(sound_path):
            print(f"[AudioManager] Error: File not found: {sound_path}")
            return False

        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(volume)
            sound.play()
            print(f"[AudioManager] Played sound: {filename}")
            return True
        except pygame.error as e:
            print(f"[AudioManager] Failed to play sound: {e}")
            return False
