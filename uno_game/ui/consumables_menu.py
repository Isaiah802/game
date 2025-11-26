"""
UI for displaying and managing food and drinks.
"""
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DirectScrolledList
from direct.showbase.ShowBase import ShowBase
from typing import Optional, List
from items import ConsumableItem, Inventory, ItemType

class ConsumablesMenu:
    """3D menu for displaying and using food and drink items using Panda3D DirectGui."""
    def __init__(self, inventory: Inventory, base=None):
        self.inventory = inventory
        self.base = base if base is not None else self._get_base()
        self.selected_item: Optional[ConsumableItem] = None
        self.scroll_offset = 0
        self.max_items_shown = 4
        self.result = None
        self._build_ui()

    def _get_base(self):
        try:
            return base
        except NameError:
            raise RuntimeError("No Panda3D ShowBase instance found. Pass 'base' to ConsumablesMenu.")

    def _build_ui(self):
        self.frame = DirectFrame(frameColor=(0.08,0.08,0.15,0.95), frameSize=(-1,1,-0.7,0.7), pos=(0,0,0))
        self.title = DirectLabel(text='Food & Drinks Inventory', scale=0.11, pos=(0,0,0.55), parent=self.frame, text_fg=(1,1,1,1))
        self.instructions = DirectLabel(text='Select an item and press Use', scale=0.07, pos=(0,0,0.45), parent=self.frame, text_fg=(0.9,0.9,0.9,1))
        self.item_list = DirectScrolledList(
            decButton_pos=(0.8, 0, 0.2),
            incButton_pos=(0.8, 0, -0.2),
            frameSize=(-0.75, 0.75, -0.3, 0.3),
            pos=(0,0,0.1),
            parent=self.frame,
            itemFrame_frameSize=(-0.7, 0.7, -0.25, 0.25),
            itemFrame_pos=(0,0,0),
            items=self._get_item_entries(),
            numItemsVisible=self.max_items_shown,
            forceHeight=0.09,
            itemText_scale=0.09
        )
        self.use_btn = DirectButton(text='Use', scale=0.08, pos=(-0.3,0,-0.45), parent=self.frame, command=self._on_use)
        self.close_btn = DirectButton(text='Close', scale=0.08, pos=(0.3,0,-0.45), parent=self.frame, command=self._on_close)

    def _get_item_entries(self):
        items = []
        for item in self.inventory.get_all_items():
            quantity = self.inventory.get_item_quantity(item.name)
            items.append(f"{item.name} x{quantity}: {item.description}")
        return items

    def _on_use(self):
        idx = self.item_list.getSelectedIndex()
        items = self.inventory.get_all_items()
        if 0 <= idx < len(items):
            self.selected_item = items[idx]
            self.result = self.selected_item
            self.frame.hide()

    def _on_close(self):
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