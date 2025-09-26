# audio/audio.py
import os
import pygame
import sys
import threading

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
        # audio_folder may be a base path or a legacy 'sounds' folder.
        if audio_folder is None:
            audio_base = base_assets
        else:
            audio_base = os.path.abspath(audio_folder)

        # Determine songs/sfx folders. Preferred layout: <assets>/songs and <assets>/sfx
        # Backwards-compatible: if the provided audio_base itself contains playable
        # files (legacy assets/sounds), use it for both songs and sfx.
        parent = audio_base
        # if user passed the 'sounds' folder directly, parent should be the assets folder
        if os.path.basename(audio_base).lower() in ('sounds', 'sound', 'audio'):
            parent = os.path.dirname(audio_base)

        self.songs_folder = os.path.join(parent, 'songs')
        self.sfx_folder = os.path.join(parent, 'sfx')

        # Legacy fallback: if audio_base contains files, use it as both folders
        if os.path.exists(audio_base) and any(f.lower().endswith(('.mp3', '.wav', '.ogg')) for f in os.listdir(audio_base)):
            self.songs_folder = audio_base
            self.sfx_folder = audio_base

        self.audio_base = audio_base
        # master sfx volume multiplier (0.0-1.0)
        self.sfx_volume = 1.0

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
        music_path = os.path.join(self.songs_folder, filename)
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
        sound_path = os.path.join(self.sfx_folder, filename)
        if not os.path.exists(sound_path):
            print(f"[AudioManager] Error: File not found: {sound_path}")
            return False

        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(max(0.0, min(1.0, volume * self.sfx_volume)))
            sound.play()
            print(f"[AudioManager] Played sound: {filename}")
            return True
        except pygame.error as e:
            print(f"[AudioManager] Failed to play sound: {e}")
            return False

    def play_sound_effect(self, filename, volume=1.0, channel_id=None):
        """Play a short, non-blocking sound effect without interrupting music.

        - filename: name of sound file in the audio folder
        - volume: 0.0-1.0
        - channel_id: optional mixer channel index to use; if None a free channel is used
        Returns the Channel object or None on failure.
        """
        if not self.available:
            print("[AudioManager] Cannot play SFX: mixer not available")
            return None

        sound_path = os.path.join(self.sfx_folder, filename)
        if not os.path.exists(sound_path):
            print(f"[AudioManager] Error: File not found: {sound_path}")
            return None

        try:
            sound = pygame.mixer.Sound(sound_path)
            # apply master sfx multiplier
            sound.set_volume(max(0.0, min(1.0, volume * self.sfx_volume)))
            if channel_id is not None:
                ch = pygame.mixer.Channel(channel_id)
                ch.play(sound)
                return ch
            else:
                return sound.play()
        except pygame.error as e:
            print(f"[AudioManager] Failed to play SFX: {e}")
            return None

    def play_sound_then_resume(self, filename, volume=1.0, fade_ms=150):
        """Pause/duck the music, play a short clip, then resume music automatically.

        This is useful for voice lines or short clips that should interrupt music
        briefly. We pause the music (not stop) so resume works correctly.
        """
        if not self.available:
            print("[AudioManager] Cannot play clip: mixer not available")
            return False

        sound_path = os.path.join(self.sfx_folder, filename)
        if not os.path.exists(sound_path):
            print(f"[AudioManager] Error: File not found: {sound_path}")
            return False

        try:
            # Pause music and play sound on a free channel
            pygame.mixer.music.pause()
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(volume)
            ch = sound.play()

            # Background thread to resume music when sound finishes
            def _wait_and_resume(channel):
                try:
                    while channel.get_busy():
                        pygame.time.wait(50)
                finally:
                    # fade-in slightly for smoothness
                    try:
                        pygame.mixer.music.unpause()
                    except Exception:
                        pass

            if ch is not None:
                t = threading.Thread(target=_wait_and_resume, args=(ch,), daemon=True)
                t.start()
                return True
            else:
                # If playing failed, resume music immediately
                pygame.mixer.music.unpause()
                return False
        except pygame.error as e:
            print(f"[AudioManager] Failed to play clip: {e}")
            try:
                pygame.mixer.music.unpause()
            except Exception:
                pass
            return False

    def change_music(self, filename, loop=True, volume=None):
        """Switch the background music to a different file."""
        if not self.available:
            print("[AudioManager] Cannot change music: mixer not available")
            return False
        if volume is not None:
            pygame.mixer.music.set_volume(volume)
        return self.play_music(filename, loop=loop, volume=pygame.mixer.music.get_volume())

    def set_music_volume(self, volume: float):
        if not self.available:
            return
        pygame.mixer.music.set_volume(volume)

    def get_music_volume(self) -> float:
        if not self.available:
            return 0.0
        return pygame.mixer.music.get_volume()

    def set_sfx_volume(self, volume: float):
        """Set a master multiplier for SFX volume (0.0-1.0)."""
        try:
            self.sfx_volume = max(0.0, min(1.0, float(volume)))
            print(f"[AudioManager] SFX volume set to {self.sfx_volume}")
        except Exception:
            pass

    def get_sfx_volume(self) -> float:
        return getattr(self, 'sfx_volume', 1.0)

