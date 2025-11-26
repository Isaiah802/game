"""
UI for changing game keybindings.
"""
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DirectScrolledList
from direct.showbase.ShowBase import ShowBase
from typing import Tuple
from settings import Settings, KEY_NAMES

class KeybindingsMenu:
    """3D Keybindings menu using Panda3D DirectGui."""
    def __init__(self, settings: Settings, base=None):
        self.settings = settings
        self.base = base if base is not None else self._get_base()
        self.selected_action = next(iter(self.settings.keybindings.keys()), None)
        self.waiting_for_key = False
        self.scroll_offset = 0
        self.max_visible_bindings = 8
        self.action_descriptions = {
            'inventory': 'Food & Drinks',
            'roll_dice': 'Roll Dice',
            'menu': 'Menu',
            'fullscreen': 'Fullscreen',
            'confirm': 'Confirm',
            'back': 'Cancel',
            'up': 'Up',
            'down': 'Down',
            'left': 'Left',
            'right': 'Right'
        }
        self.result = None
        self._build_ui()

    def _get_base(self):
        try:
            return base
        except NameError:
            raise RuntimeError("No Panda3D ShowBase instance found. Pass 'base' to KeybindingsMenu.")

    def _build_ui(self):
        self.frame = DirectFrame(frameColor=(0.08,0.08,0.15,0.95), frameSize=(-1,1,-0.7,0.7), pos=(0,0,0))
        self.title = DirectLabel(text='Keybindings', scale=0.11, pos=(0,0,0.55), parent=self.frame, text_fg=(1,1,1,1))
        self.instructions = DirectLabel(text='Select an action and press Change to rebind', scale=0.07, pos=(0,0,0.45), parent=self.frame, text_fg=(0.9,0.9,0.9,1))
        self.binding_list = DirectScrolledList(
            decButton_pos=(0.8, 0, 0.2),
            incButton_pos=(0.8, 0, -0.2),
            frameSize=(-0.75, 0.75, -0.3, 0.3),
            pos=(0,0,0.1),
            parent=self.frame,
            itemFrame_frameSize=(-0.7, 0.7, -0.25, 0.25),
            itemFrame_pos=(0,0,0),
            items=self._get_binding_items(),
            numItemsVisible=self.max_visible_bindings,
            forceHeight=0.07,
            itemText_scale=0.07
        )
        self.change_btn = DirectButton(text='Change', scale=0.08, pos=(-0.3,0,-0.45), parent=self.frame, command=self._on_change)
        self.reset_btn = DirectButton(text='Reset', scale=0.08, pos=(0,0,-0.45), parent=self.frame, command=self._on_reset)
        self.back_btn = DirectButton(text='Back', scale=0.08, pos=(0.3,0,-0.45), parent=self.frame, command=self._on_back)

    def _get_binding_items(self):
        items = []
        for action, key in self.settings.keybindings.items():
            desc = self.action_descriptions.get(action, action.replace('_', ' ').title())
            key_name = self.settings.get_key_name(key)
            items.append(f"{desc}: {key_name}")
        return items

    def _on_change(self):
        idx = self.binding_list.getSelectedIndex()
        actions = list(self.settings.keybindings.keys())
        if 0 <= idx < len(actions):
            self.selected_action = actions[idx]
            self.waiting_for_key = True
            self.instructions['text'] = f"Press any key to bind {self.action_descriptions.get(self.selected_action, self.selected_action)}"
            self.base.accept('arrow_up', self._on_key, ['arrow_up'])
            self.base.accept('arrow_down', self._on_key, ['arrow_down'])
            self.base.accept('arrow_left', self._on_key, ['arrow_left'])
            self.base.accept('arrow_right', self._on_key, ['arrow_right'])
            self.base.accept('enter', self._on_key, ['enter'])
            self.base.accept('escape', self._on_cancel)

    def _on_key(self, key_name):
        if self.waiting_for_key and self.selected_action:
            self.settings.set_key(self.selected_action, key_name)
            self.waiting_for_key = False
            self.instructions['text'] = 'Select an action and press Change to rebind'
            self.binding_list['items'] = self._get_binding_items()
            self.base.ignoreAll()

    def _on_cancel(self):
        self.waiting_for_key = False
        self.instructions['text'] = 'Select an action and press Change to rebind'
        self.base.ignoreAll()

    def _on_reset(self):
        self.settings.reset_keybindings()
        self.binding_list['items'] = self._get_binding_items()

    def _on_back(self):
        self.result = 'back'
        self.frame.hide()

    def show(self):
        self.frame.show()
        self.result = None

    def run(self):
        self.show()
        while self.result is None:
            self.base.taskMgr.step()
        return self.result
    
    # All input and rendering is now handled by Panda3D DirectGui. Obsolete pygame-based methods removed.