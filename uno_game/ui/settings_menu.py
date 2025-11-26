from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval
from panda3d.core import NodePath, Texture

class SettingsHamburgerMenu:
    """
    Advanced 3D hamburger menu for settings, with icons and slide-in animation.
    Buttons: Audio, Keybindings, Change Song, Back
    Usage:
        menu = SettingsHamburgerMenu(base)
        result = menu.run()  # returns selected submenu or None
    """
    def __init__(self, base, icon_textures=None):
        self.base = base
        self.result = None
        self.frame = None
        self.icon_textures = icon_textures or {}
        self._build_ui()
        self._setup_animated_background()
        self._load_sounds()
    def _setup_animated_background(self):
        # Add floating icons (audio/keybindings/song/back) as animated OnscreenImages
        from direct.gui.OnscreenImage import OnscreenImage
        from panda3d.core import TransparencyAttrib
        import math, random
        self.bg_elements = []
        icon_paths = [self.icon_textures.get('audio'), self.icon_textures.get('keybindings'), self.icon_textures.get('song'), self.icon_textures.get('back')]
        for i, img in enumerate(icon_paths):
            if img:
                elem = OnscreenImage(image=img, pos=(random.uniform(-0.4,0.4), 0, random.uniform(-0.5,0.5)), scale=0.09, parent=self.frame)
                elem.setTransparency(TransparencyAttrib.MAlpha)
                self.bg_elements.append(elem)
        def animate_bg(task):
            t = task.time
            for i, elem in enumerate(self.bg_elements):
                elem.setPos(math.sin(t + i)*0.4, 0, math.cos(t + i*1.5)*0.5)
            return task.cont
        self.base.taskMgr.add(animate_bg, 'settings_animate_bg')

    def _load_sounds(self):
        # Load sound effects for button clicks
        try:
            from audio.audio import AudioManager
            self.audio = AudioManager(audio_folder='assets/sounds')
            self.click_sound = 'menu_click.wav'  # Example sound file
        except Exception:
            self.audio = None
            self.click_sound = None

    def _build_ui(self):
        self.frame = DirectFrame(frameColor=(0.09,0.09,0.18,0.95), frameSize=(-0.5,0.5,-0.7,0.7), pos=(-1.0,0,0))
        self.title = DirectLabel(text='Settings', scale=0.11, pos=(0,0,0.55), parent=self.frame, text_fg=(1,1,1,1))
        self.buttons = []
        btn_info = [
            ('Audio', 'audio', self.icon_textures.get('audio')),
            ('Keybindings', 'keybindings', self.icon_textures.get('keybindings')),
            ('Change Song', 'change_song', self.icon_textures.get('song')),
            ('Back', 'back', self.icon_textures.get('back')),
        ]
        gap = 0.25
        for i, (text, key, icon) in enumerate(btn_info):
            btn = DirectButton(
                text=text,
                scale=0.09,
                pos=(-0.15,0,0.35-gap*i),
                parent=self.frame,
                command=lambda k=key: self._play_click_sound(k),
                frameColor=(0.8,0.8,0.8,1),
                text_fg=(0,0,0,1),
                relief=1
            )
            if icon:
                btn['geom'] = icon
                btn['geom_scale'] = (0.08, 1, 0.08)
                btn['geom_pos'] = (-0.32, 0, 0)
            self.buttons.append(btn)

    def _play_click_sound(self, key):
        if self.audio and self.click_sound:
            self.audio.play_sfx(self.click_sound)
        self._on_select(key)

    def show(self):
        self.frame.show()
        self.result = None
        # Slide-in animation
        Sequence(
            LerpPosInterval(self.frame, 0.4, (0,0,0), startPos=(-1.0,0,0))
        ).start()

    def hide(self):
        # Slide-out animation
        Sequence(
            LerpPosInterval(self.frame, 0.3, (-1.0,0,0), startPos=(0,0,0)),
        ).start()

    def _on_select(self, key):
        self.result = key
        self.hide()

    def run(self):
        self.show()
        while self.result is None:
            self.base.taskMgr.step()
        return self.result
