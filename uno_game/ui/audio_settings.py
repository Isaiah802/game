from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectSlider, DirectButton

class AudioSettingsMenu:
    """3D audio settings menu using Panda3D DirectGui."""
    def __init__(self, audio_manager, width=1.5, height=1.0, base=None):
        self.am = audio_manager
        self.width = width
        self.height = height
        try:
            self.music_vol = float(self.am.get_music_volume())
        except Exception:
            self.music_vol = 0.5
        try:
            self.sfx_vol = float(self.am.get_sfx_volume())
        except Exception:
            self.sfx_vol = 1.0
        self.result = None
        self.base = base if base is not None else self._get_base()
        self._build_ui()

    def _get_base(self):
        try:
            return base
        except NameError:
            raise RuntimeError("No Panda3D ShowBase instance found. Pass 'base' to AudioSettingsMenu.")

    def _build_ui(self):
        self.frame = DirectFrame(frameColor=(0.15,0.12,0.12,0.95), frameSize=(-self.width/2,self.width/2,-self.height/2,self.height/2), pos=(0,0,0))
        self.title = DirectLabel(text='Audio Settings', scale=0.12, pos=(0,0,self.height/2-0.18), parent=self.frame, text_fg=(1,1,1,1))
        self.music_slider = DirectSlider(
            range=(0,1), value=self.music_vol, pageSize=0.01,
            pos=(-0.4,0,0.15), scale=0.6, parent=self.frame,
            command=self._on_music_change
        )
        self.music_label = DirectLabel(text=f'Music Volume: {int(self.music_vol*100)}%', scale=0.08, pos=(0.3,0,0.15), parent=self.frame, text_fg=(1,1,1,1))
        self.sfx_slider = DirectSlider(
            range=(0,1), value=self.sfx_vol, pageSize=0.01,
            pos=(-0.4,0,-0.15), scale=0.6, parent=self.frame,
            command=self._on_sfx_change
        )
        self.sfx_label = DirectLabel(text=f'SFX Volume: {int(self.sfx_vol*100)}%', scale=0.08, pos=(0.3,0,-0.15), parent=self.frame, text_fg=(1,1,1,1))
        self.save_btn = DirectButton(text='Save', scale=0.09, pos=(-0.2,0,-self.height/2+0.18), parent=self.frame, command=self._on_save)
        self.cancel_btn = DirectButton(text='Cancel', scale=0.09, pos=(0.2,0,-self.height/2+0.18), parent=self.frame, command=self._on_cancel)

    def _on_music_change(self):
        self.music_vol = self.music_slider['value']
        self.music_label['text'] = f'Music Volume: {int(self.music_vol*100)}%'
        try:
            self.am.set_music_volume(self.music_vol)
        except Exception:
            pass

    def _on_sfx_change(self):
        self.sfx_vol = self.sfx_slider['value']
        self.sfx_label['text'] = f'SFX Volume: {int(self.sfx_vol*100)}%'
        try:
            self.am.set_sfx_volume(self.sfx_vol)
        except Exception:
            pass

    def _on_save(self):
        self.result = {
            'music_volume': self.music_vol,
            'sfx_volume': self.sfx_vol
        }
        self.frame.hide()

    def _on_cancel(self):
        self.result = None
        self.frame.hide()

    def show(self):
        self.frame.show()
        self.result = None

    def run(self):
        self.show()
        while self.result is None:
            self.base.taskMgr.step()
        return self.result
