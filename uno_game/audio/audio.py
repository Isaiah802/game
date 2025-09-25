# audio/audio.py
import os
import pygame
import sys

# ---------------- Audio Manager ----------------
class AudioManager:
    def __init__(self, audio_folder=None):
        """
        Initialize the AudioManager.
        If audio_folder is None, tries 'assets/sound' first, then 'assets/audio'.
        """
        base_assets = os.path.join(os.path.dirname(__file__), '..', 'assets')
        if audio_folder is None:
            preferred = os.path.join(base_assets, 'sounds')
            fallback = os.path.join(base_assets, 'audio')
            audio_folder = preferred if os.path.exists(preferred) else fallback

        self.audio_folder = os.path.abspath(audio_folder)

        # Initialize pygame mixer safely
        try:
            pygame.init()
            pygame.mixer.init()
        except pygame.error as e:
            print(f"[AudioManager] Pygame mixer init failed: {e}")
            sys.exit(1)

    def play_music(self, filename, loop=True, volume=0.5):
        """Play background music indefinitely or once"""
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
        pygame.mixer.music.stop()
        print("[AudioManager] Music stopped")

    def play_sound(self, filename, volume=0.5):
        """Play a short sound effect"""
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
