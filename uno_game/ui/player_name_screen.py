from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectEntry, DirectButton


class PlayerNameScreen:
    """Simple DirectGui screen to collect player names.

    Usage: screen = PlayerNameScreen(base=base); names = screen.run()
    Returns a list of names (strings) or [] if cancelled.
    """

    def __init__(self, base=None, max_players: int = 6):
        self.base = base
        self.max_players = max_players
        self.frame = DirectFrame(frameColor=(0.08, 0.08, 0.12, 0.95), frameSize=(-1.0, 1.0, -0.9, 0.9), pos=(0, 0, 0))
        self.title = DirectLabel(text="Enter Player Names", scale=0.12, pos=(0, 0, 0.75), parent=self.frame, text_fg=(1, 1, 1, 1))
        self.entries = []
        self._build_initial_entries()
        self.continue_btn = DirectButton(text="Continue", scale=0.08, pos=(0.3, 0, -0.8), parent=self.frame, command=self._on_continue)
        self.add_btn = DirectButton(text="Add Player", scale=0.06, pos=(-0.3, 0, -0.8), parent=self.frame, command=self._on_add_player)
        self.result = None
        self._warning = None

    def _build_initial_entries(self):
        # start with two player name entries
        start_y = 0.4
        gap = 0.18
        for i in range(2):
            self._create_entry(i, start_y - i * gap)

    def _create_entry(self, idx: int, y: float):
        label = DirectLabel(text=f"Player {idx+1}:", scale=0.07, pos=(-0.5, 0, y), parent=self.frame, text_fg=(1, 1, 1, 1))
        entry = DirectEntry(text_fg=(1,1,1,1), scale=0.06, pos=(-0.15, 0, y), parent=self.frame, width=12, initialText=f"Player{idx+1}", numLines=1)
        self.entries.append(entry)

    def _on_add_player(self):
        if len(self.entries) >= self.max_players:
            return
        idx = len(self.entries)
        y = 0.4 - idx * 0.18
        self._create_entry(idx, y)

    def _on_continue(self):
        names = [e.get() for e in self.entries]
        # strip and remove empty
        names = [n.strip() for n in names if n and n.strip()]
        if len(names) < 2:
            # show a warning label
            if self._warning is None:
                self._warning = DirectLabel(text="Please enter at least two player names.", scale=0.06, pos=(0, 0, -0.65), parent=self.frame, text_fg=(1, 0.4, 0.4, 1))
            return
        self.result = names
        self.frame.hide()

    def show(self):
        self.frame.show()
        self.result = None

    def run(self):
        self.show()
        # loop until the user completes the form
        while self.result is None:
            # step the Panda task manager so GUI stays responsive
            try:
                self.base.taskMgr.step()
            except Exception:
                # If no base provided or stepping fails, break to avoid infinite loop
                break
        return self.result or []
