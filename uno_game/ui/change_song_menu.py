import os
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DirectScrolledList
from typing import List, Optional


class ChangeSongMenu:
    """3D menu to pick a music file from the audio folder using Panda3D DirectGui."""
    def __init__(self, audio_folder: str, audio_manager=None, base=None):
        self.audio = audio_manager
        if audio_manager is not None and hasattr(audio_manager, 'songs_folder'):
            self.audio_folder = audio_manager.songs_folder
        else:
            self.audio_folder = audio_folder
        self.base = base if base is not None else self._get_base()
        self.files: List[str] = []
        self.selected = 0
        self.result = None
        self._last_preview_index = None
        self._load_files()
        self._build_ui()

    def _get_base(self):
        try:
            return base
        except NameError:
            raise RuntimeError("No Panda3D ShowBase instance found. Pass 'base' to ChangeSongMenu.")

    def _load_files(self):
        if not os.path.exists(self.audio_folder):
            self.files = []
            return
        self.files = [f for f in os.listdir(self.audio_folder) if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
        self.files.sort()
        if not self.files:
            self.selected = 0

    def _build_ui(self):
        self.frame = DirectFrame(frameColor=(0.09,0.09,0.18,0.95), frameSize=(-1,1,-0.7,0.7), pos=(0,0,0))
        self.title = DirectLabel(text='Select Music', scale=0.12, pos=(0,0,0.55), parent=self.frame, text_fg=(1,1,1,1))
        self.song_list = DirectScrolledList(
            decButton_pos=(0.8, 0, 0.2),
            incButton_pos=(0.8, 0, -0.2),
            frameSize=(-0.75, 0.75, -0.3, 0.3),
            pos=(0,0,0.1),
            parent=self.frame,
            itemFrame_frameSize=(-0.7, 0.7, -0.25, 0.25),
            itemFrame_pos=(0,0,0),
            items=self.files if self.files else ['No music files found in folder.'],
            numItemsVisible=8,
            forceHeight=0.07,
            itemText_scale=0.07
        )
        self.play_btn = DirectButton(text='Play', scale=0.08, pos=(-0.3,0,-0.45), parent=self.frame, command=self._on_play)
        self.cancel_btn = DirectButton(text='Cancel', scale=0.08, pos=(0.3,0,-0.45), parent=self.frame, command=self._on_cancel)
        self.instructions = DirectLabel(text='Select a song and press Play, or Cancel', scale=0.07, pos=(0,0,-0.6), parent=self.frame, text_fg=(0.8,0.8,0.8,1))

    def _on_play(self):
        idx = self.song_list.getSelectedIndex()
        if self.files and 0 <= idx < len(self.files):
            self.selected = idx
            self._maybe_preview()
            self.result = self.files[self.selected]
            self.frame.hide()
        else:
            self.result = None
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

    def _maybe_preview(self):
        """Play a short preview when the highlighted selection changes."""
        if self.audio is None:
            return
        if not self.files:
            return
        if self._last_preview_index == self.selected:
            return
        self._last_preview_index = self.selected
        fname = self.files[self.selected]
        try:
            # play non-looping preview
            self.audio.play_music(fname, loop=False, volume=0.6)
        except Exception:
            pass
