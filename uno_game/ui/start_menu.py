
# Panda3D 3D Start Menu using DirectGui
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel

class StartMenu:
    def __init__(self, width=1.5, height=1.0, base=None):
        self.width = width
        self.height = height
        self.result = None
        self.base = base if base is not None else self._get_base()
        self.frame = DirectFrame(frameColor=(0.1,0.2,0.1,0.95), frameSize=(-width/2,width/2,-height/2,height/2), pos=(0,0,0))
        self.title = DirectLabel(text="Game - Start Menu", scale=0.12, pos=(0,0,height/2-0.18), parent=self.frame, text_fg=(1,1,1,1))
        self.buttons = []
        self._build_buttons()
        self._setup_animated_background()
        self._load_sounds()
    def _setup_animated_background(self):
        # Add floating dice/chips as animated OnscreenImages
        from direct.gui.OnscreenImage import OnscreenImage
        from panda3d.core import TransparencyAttrib
        import math, random
        self.bg_elements = []
        dice_img = 'assets/cards/dice/dice1.png'  # Example dice image path
        chip_img = 'assets/cards/chips.png'       # Example chip image path
        for i in range(3):
            img_path = dice_img if i % 2 == 0 else chip_img
            elem = OnscreenImage(image=img_path, pos=(random.uniform(-0.7,0.7), 0, random.uniform(-0.3,0.3)), scale=0.12, parent=self.frame)
            elem.setTransparency(TransparencyAttrib.MAlpha)
            self.bg_elements.append(elem)
        # Animate elements in a task
        def animate_bg(task):
            t = task.time
            for i, elem in enumerate(self.bg_elements):
                elem.setPos(math.sin(t + i)*0.7, 0, math.cos(t + i*1.5)*0.3)
            return task.cont
        self.base.taskMgr.add(animate_bg, 'animate_bg')

    def _load_sounds(self):
        # Load sound effects for button clicks
        try:
            from audio.audio import AudioManager
            self.audio = AudioManager(audio_folder='assets/sounds')
            self.click_sound = 'menu_click.wav'  # Example sound file
        except Exception:
            self.audio = None
            self.click_sound = None

    def _get_base(self):
        try:
            return base
        except NameError:
            raise RuntimeError("No Panda3D ShowBase instance found. Pass 'base' to StartMenu.")

    def _build_buttons(self):
        btn_texts = [
            ("Play", 'play'),
            ("Audio Settings", 'settings'),
            ("Change Song", 'change_song'),
            ("Keybindings", 'keybindings'),
            ("Local WiFi Play (Coming Soon)", 'multiplayer_soon'),
            ("Quit", 'quit'),
        ]
        gap = 0.18
        for i, (text, key) in enumerate(btn_texts):
            btn = DirectButton(
                text=text,
                scale=0.09,
                pos=(0,0,self.height/2-0.35-gap*i),
                parent=self.frame,
                command=lambda k=key: self._on_select(k),
                frameColor=(0.2,0.2,0.3,1),
                text_fg=(0.95,0.95,0.95,1),
                pressEffect=1,
                relief=1,
                borderWidth=(0.02,0.02)
            )
            from direct.gui.DirectGui import DGG
            btn.bind(DGG.ENTER, lambda e, b=btn: b.setColor((0.3,0.4,0.6,1), 1))
            btn.bind(DGG.EXIT, lambda e, b=btn: b.setColor((0.2,0.2,0.3,1), 1))
            btn.bind(DGG.B1PRESS, lambda e, b=btn: b.setColor((0.5,0.5,0.7,1), 1))
            btn.bind(DGG.B1RELEASE, lambda e, b=btn: b.setColor((0.3,0.4,0.6,1), 1))
            # Play sound on click
            btn['command'] = lambda k=key: self._play_click_sound(k)
            self.buttons.append(btn)

    def _play_click_sound(self, key):
        if self.audio and self.click_sound:
            self.audio.play_sfx(self.click_sound)
        self._on_select(key)

    def _on_select(self, key):
        self.result = key
        self.frame.hide()

    def show(self):
        self.frame.show()
        self.result = None

    def run(self):
        self.show()
        # Wait for user selection
        while self.result is None:
            self.base.taskMgr.step()
        return self.result
