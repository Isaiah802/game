"""
UI for the food and drink shop.
"""
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DirectScrolledList
from direct.showbase.ShowBase import ShowBase
from items import ConsumableItem, registry
from settings import Settings

class ShopMenu:
    """3D shop menu using Panda3D DirectGui."""
    def __init__(self, player_chips: int, settings: Settings, base=None):
        self.player_chips = player_chips
        self.settings = settings
        self.selected_item = None
        self.message = ""
        self.result = None
        self.base = base if base is not None else self._get_base()
        self._build_ui()

    def _get_base(self):
        # Try to get the global base instance
        from direct.showbase.ShowBase import ShowBase
        return ShowBase()

    def _build_ui(self):
        self.frame = DirectFrame(frameColor=(0.08,0.08,0.15,0.95), frameSize=(-1,1,-0.7,0.7), pos=(0,0,0))
        self.title = DirectLabel(text='Shop - Buy Food & Drinks', scale=0.11, pos=(0,0,0.55), parent=self.frame, text_fg=(1,1,1,1))
        self.chips_label = DirectLabel(text=f'Chips: {self.player_chips}', scale=0.09, pos=(-0.7,0,0.45), parent=self.frame, text_fg=(1,1,0.5,1))
        self.message_label = DirectLabel(text='', scale=0.08, pos=(0,0,-0.55), parent=self.frame, text_fg=(1,1,1,1))
        items = registry.get_all_items()
        self.item_names = [f"{item.name} ({item.cost} chips)" for item in items]
        self.item_list = DirectScrolledList(
            decButton_pos=(0.8, 0, 0.2), incButton_pos=(0.8, 0, -0.2),
            frameSize=(-0.8,0.8,-0.2,0.2), pos=(0,0,0.2), parent=self.frame,
            itemFrame_frameSize=(-0.7,0.7,-0.18,0.18), itemFrame_pos=(0,0,0),
            numItemsVisible=5,
            items=[DirectButton(text=name, scale=0.08, command=lambda i=i: self._on_select(items[i]), parent=self.frame) for i, name in enumerate(self.item_names)]
        )
        self.buy_btn = DirectButton(text='Buy', scale=0.09, pos=(-0.3,0,-0.6), parent=self.frame, command=self._on_buy)
        self.cancel_btn = DirectButton(text='Cancel', scale=0.09, pos=(0.3,0,-0.6), parent=self.frame, command=self._on_cancel)

    def _on_select(self, item):
        self.selected_item = item
        self.message_label['text'] = f"Selected: {item.name} - {item.description}"

    def _on_buy(self):
        if self.selected_item:
            if self.player_chips >= self.selected_item.cost:
                self.player_chips -= self.selected_item.cost
                self.chips_label['text'] = f'Chips: {self.player_chips}'
                self.message_label['text'] = f"Bought {self.selected_item.name}!"
                self.result = self.selected_item
                self.frame.hide()
            else:
                self.message_label['text'] = "Not enough chips!"
        else:
            self.message_label['text'] = "Select an item first."

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