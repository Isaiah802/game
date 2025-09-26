import os
import sys
import types
import builtins
import pytest

# Ensure repo root is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cards import card
# Note: do not import AudioManager at module import time because it imports pygame.
AudioManager = None
import os
import sys
import types
import unittest

# Ensure repo root is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Provide a fake pygame module early so imports don't initialize the real SDL
class DummyChannel:
    def get_busy(self):
        return False


class DummySound:
    def __init__(self, path):
        self.path = path

    def set_volume(self, v):
        pass

    def play(self):
        return DummyChannel()


class DummyMixerMusic:
    def __init__(self):
        self._volume = 0.5

    def load(self, path):
        self._path = path

    def set_volume(self, v):
        self._volume = v

    def play(self, loops):
        self._playing = True

    def stop(self):
        self._playing = False

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False


fake = types.SimpleNamespace()
fake.error = Exception
fake.mixer = types.SimpleNamespace()
fake.mixer.Sound = lambda path: DummySound(path)
fake.mixer.music = DummyMixerMusic()
fake.mixer.init = lambda: None
fake.init = lambda: None
fake.Rect = lambda *a, **k: object()
fake.draw = types.SimpleNamespace(rect=lambda *a, **k: None)
fake.font = types.SimpleNamespace(SysFont=lambda *a, **k: types.SimpleNamespace(render=lambda *a, **k: types.SimpleNamespace(get_rect=lambda **k: types.SimpleNamespace())))

sys.modules['pygame'] = fake

from cards import card
from audio.audio import AudioManager


class DummyChannel:
    def __init__(self):
        self._busy = True

    def play(self, sound):
        self._busy = True

    def get_busy(self):
        return False

import os
import sys
import types
import unittest

# Ensure repo root is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cards import card


class DummyChannel:
    def play(self, sound):
        pass

    def get_busy(self):
        return False


class DummySound:
    def __init__(self, path):
        self.path = path

    def set_volume(self, v):
        pass

    def play(self):
        return DummyChannel()


class DummyMixerMusic:
    def __init__(self):
        self._volume = 0.5
        self._paused = False

    def load(self, path):
        self._path = path

    def set_volume(self, v):
        self._volume = v

    def play(self, loops):
        self._playing = True

    def stop(self):
        self._playing = False

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False


class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Patch a fake pygame module into sys.modules to avoid needing an actual display
        fake = types.SimpleNamespace()
        fake.mixer = types.SimpleNamespace()
        fake.mixer.Sound = lambda path: DummySound(path)
        fake.mixer.music = DummyMixerMusic()
        fake.mixer.init = lambda: None
        fake.init = lambda: None
        fake.Rect = lambda *a, **k: object()
        fake.draw = types.SimpleNamespace(rect=lambda *a, **k: None)
        fake.font = types.SimpleNamespace(SysFont=lambda *a, **k: types.SimpleNamespace(render=lambda *a, **k: types.SimpleNamespace(get_rect=lambda **k: types.SimpleNamespace())))

        sys.modules['pygame'] = fake

    def tearDown(self):
        # Remove the fake pygame module
        if 'pygame' in sys.modules:
            del sys.modules['pygame']

    def test_create_uno_deck(self):
        deck = card.create_uno_deck()
        self.assertIsInstance(deck, list)
        self.assertTrue(any(c['color'] == 'Red' for c in deck))
        self.assertTrue(any(c['type'] == 'Wild' for c in deck))

    def test_audio_manager_basic(self):
        import tempfile
        tmpdir = tempfile.TemporaryDirectory()
        # new layout: songs/ and sfx/ folders
        songs_folder = os.path.join(tmpdir.name, 'songs')
        sfx_folder = os.path.join(tmpdir.name, 'sfx')
        os.makedirs(songs_folder, exist_ok=True)
        os.makedirs(sfx_folder, exist_ok=True)
        fake_song = os.path.join(songs_folder, 'test.mp3')
        with open(fake_song, 'wb') as f:
            f.write(b'FAKE_MP3')
        fake_sfx = os.path.join(sfx_folder, 'click.wav')
        with open(fake_sfx, 'wb') as f:
            f.write(b'FAKE_WAV')

        # import AudioManager after pygame has been mocked
        from audio.audio import AudioManager as _AudioManager
        # pass the parent (tmpdir) so AudioManager resolves songs/sfx
        am = _AudioManager(audio_folder=tmpdir.name)
        self.assertTrue(hasattr(am, 'play_music'))

        ok = am.play_music('test.mp3', loop=False, volume=0.3)
        self.assertTrue(ok)

        # play a sound effect from the sfx folder
        ch = am.play_sound_effect('click.wav', volume=0.9)
        # our DummySound.play returns DummyChannel; ensure no exception
        self.assertIsNotNone(ch)

        # test play_sound_then_resume using sfx
        res = am.play_sound_then_resume('click.wav', volume=0.8)
        self.assertIsInstance(res, bool)

        am.stop_music()

    def test_draw_uno_card_pygame_calls_surface_methods(self):
        class FakeSurface:
            def __init__(self):
                self.ops = []

            def blit(self, src, rect):
                self.ops.append(('blit', src, rect))

        surface = FakeSurface()
        sample_card = {'color': 'Blue', 'type': '7'}
        # Should not raise
        card.draw_uno_card_pygame(surface, 10, 20, sample_card)
        self.assertTrue(any(op[0] == 'blit' for op in surface.ops))


if __name__ == '__main__':
    unittest.main()

