"""
Visual display for active status effects on players.
"""
from direct.gui.DirectGui import DirectFrame, DirectLabel
from direct.showbase.ShowBase import ShowBase
from items.consumables import Effect


class StatusDisplay:
    """Displays active status effects for players using Panda3D DirectGui."""
    EFFECT_INFO = {
        Effect.ENERGY_BOOST: {
            'color': (1, 0.84, 0),  # Gold
            'symbol': '⚡',
            'short_name': 'Energy'
        },
        Effect.LUCK_BOOST: {
            'color': (0, 1, 0.5),  # Spring green
            'symbol': '🍀',
            'short_name': 'Luck'
        },
        Effect.FOCUS_BOOST: {
            'color': (0.39, 0.58, 0.93),  # Cornflower blue
            'symbol': '🎯',
            'short_name': 'Focus'
        },
        Effect.MOOD_BOOST: {
            'color': (1, 0.41, 0.7),  # Hot pink
            'symbol': '😊',
            'short_name': 'Mood'
        }
    }

    def __init__(self, base=None):
        self.base = base if base is not None else self._get_base()
        self.labels = []
        self.frame = None

    def _get_base(self):
        try:
            return base
        except NameError:
            raise RuntimeError("No Panda3D ShowBase instance found. Pass 'base' to StatusDisplay.")

    def show_player_effects(self, player_name: str, active_effects: dict, pos=(0,0), compact=False):
        if self.frame:
            self.frame.destroy()
        self.frame = DirectFrame(frameColor=(0.08,0.08,0.15,0.95), frameSize=(-0.7,0.7,-0.2,0.2), pos=(pos[0],0,pos[1]))
        x = -0.65
        y = 0.12
        for effect, turns_left in active_effects.items():
            if effect not in self.EFFECT_INFO:
                continue
            info = self.EFFECT_INFO[effect]
            label_text = f"{info['symbol']} {info['short_name']}: {turns_left} turns"
            label = DirectLabel(text=label_text, scale=0.07, pos=(x,0,y), parent=self.frame, text_fg=info['color']+(1,))
            self.labels.append(label)
            y -= 0.09

    def show_all_players_effects(self, game_manager, pos=(0,0)):
        if self.frame:
            self.frame.destroy()
        self.frame = DirectFrame(frameColor=(0.08,0.08,0.15,0.95), frameSize=(-0.7,0.7,-0.6,0.6), pos=(pos[0],0,pos[1]))
        y = 0.55
        title = DirectLabel(text='Active Effects:', scale=0.08, pos=(-0.65,0,y), parent=self.frame, text_fg=(1,1,1,1))
        y -= 0.09
        for player_name in game_manager.player_order:
            effects = game_manager.get_active_effects(player_name)
            if effects:
                name_label = DirectLabel(text=f"{player_name}:", scale=0.07, pos=(-0.6,0,y), parent=self.frame, text_fg=(0.8,0.8,0.8,1))
                y -= 0.07
                for effect, turns_left in effects.items():
                    info = self.EFFECT_INFO.get(effect)
                    if info:
                        label_text = f"{info['symbol']} {info['short_name']}: {turns_left} turns"
                        DirectLabel(text=label_text, scale=0.07, pos=(-0.55,0,y), parent=self.frame, text_fg=info['color']+(1,))
                        y -= 0.07
                y -= 0.04

def show_compact_player_status(player_name: str, chips: int, active_effects: dict, pos=(0,0), base=None):
    frame = DirectFrame(frameColor=(0.16,0.16,0.25,0.95), frameSize=(-0.4,0.4,-0.08,0.08), pos=(pos[0],0,pos[1]))
    text = f"{player_name}: {chips} chips"
    DirectLabel(text=text, scale=0.07, pos=(-0.35,0,0.04), parent=frame, text_fg=(1,1,1,1))
    x = -0.35
    y = -0.02
    for effect, turns_left in active_effects.items():
        info = StatusDisplay.EFFECT_INFO.get(effect)
        if info:
            label_text = f"{info['symbol']} {turns_left}"
            DirectLabel(text=label_text, scale=0.06, pos=(x,0,y), parent=frame, text_fg=info['color']+(1,))
            x += 0.13
