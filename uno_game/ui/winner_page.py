import os
import time
from direct.gui.DirectGui import DirectFrame, DirectLabel


class WinnerScreen:
    """3D winner screen using Panda3D DirectGui."""
    def __init__(self, winner_name: str = 'Player', message: str = 'You win!', duration: float = 3.0, base=None, audio_manager=None):
        self.winner_name = winner_name
        self.message = message
        self.duration = duration
        self.base = base if base is not None else self._get_base()
        self.audio_manager = audio_manager
        self.result = None
        self.frame = None

    def _get_base(self):
        try:
            return base
        except NameError:
            raise RuntimeError("No Panda3D ShowBase instance found. Pass 'base' to WinnerScreen.")

    def show(self):
        if self.frame:
            self.frame.destroy()
        self.frame = DirectFrame(frameColor=(0.16,0.08,0.24,0.95), frameSize=(-1,1,-0.7,0.7), pos=(0,0,0))
        self.title = DirectLabel(text=f'{self.winner_name} Wins!', scale=0.15, pos=(0,0,0.2), parent=self.frame, text_fg=(1,0.84,0,1))
        self.subtitle = DirectLabel(text=self.message, scale=0.09, pos=(0,0,0.05), parent=self.frame, text_fg=(0.86,0.86,0.86,1))
        self.continue_btn = DirectButton(text='Continue', scale=0.09, pos=(0,0,-0.3), parent=self.frame, command=self._on_continue)
        # Optional: play victory sound
        if self.audio_manager is not None:
            try:
                sfx_path = os.path.join(self.audio_manager.sfx_folder, 'victory.mp3')
                if os.path.exists(sfx_path):
                    self.audio_manager.play_sfx('victory.mp3', volume=0.8)
            except Exception:
                pass

    def _on_continue(self):
        self.result = True
        self.frame.hide()

    def run(self):
        self.show()
        start = time.time()
        while self.result is None and (time.time() - start) < self.duration:
            self.base.taskMgr.step()
        self.frame.hide()
        return self.result
