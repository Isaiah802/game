import os
import sys
import json
import random
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from ui.start_menu import StartMenu
from ui.settings_menu import SettingsHamburgerMenu
from ui.audio_settings import AudioSettingsMenu
from ui.keybindings_menu import KeybindingsMenu
from ui.change_song_menu import ChangeSongMenu
from audio.audio import AudioManager
from settings.keybindings import Settings

BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
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

def main():
    base = ShowBase()
    audio = AudioManager(audio_folder=ASSETS_DIR)

    props = WindowProperties()
    props.setTitle("Zanzibar Dice Game")
    icon_path = os.path.join(ASSETS_DIR, "ach_demo.png")
    if os.path.exists(icon_path):
        try:
            from panda3d.core import PNMImage
            icon_img = PNMImage()
            if icon_img.read(icon_path):
                props.setIconFilename(icon_path)
        except Exception:
            pass
    props.setFullscreen(False)
    base.win.requestProperties(props)

    def toggle_fullscreen():
        wp = WindowProperties()
        wp.setFullscreen(not base.win.isFullscreen())
        base.win.requestProperties(wp)
    base.accept('f', toggle_fullscreen)

    from direct.interval.IntervalGlobal import LerpColorScaleInterval
    base.render.setColorScale(0, 0, 0, 1)
    fade_in = LerpColorScaleInterval(base.render, 1.2, (1, 1, 1, 1))
    fade_in.start()

    menu = StartMenu(base=base)
    try:
        from ui.intro_screen import IntroScreen
        intro = IntroScreen(title='Zanzibar', subtitle='A Dice Game by I paid $1,152.60 to have this team name', duration=5.0)
        intro.run()
    except Exception:
        pass

    settings = load_settings()
    game_settings = Settings()
    try:
        audio.set_sfx_volume(settings.get('sfx_volume', 1.0))
    except Exception:
        pass
    music_file = settings.get('music_file', 'test.mp3')
    music_vol = settings.get('music_volume', 0.6)
    audio.play_music(music_file, loop=True, volume=music_vol)

    choice = menu.run()
    # ...existing menu choice logic...

    base.run()

if __name__ == '__main__':
    main()
