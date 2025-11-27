import typing
from typing import Dict, List
import pygame
try:
    from graphics.achivments import notifier
except Exception:
    # Fallback no-op notifier to avoid import-time failures when pygame isn't
    # initialized or graphics module cannot be imported.
    class _DummyNotifier:
        def show(self, *a, **k):
            return
        def update(self, *a, **k):
            return
        def draw(self, *a, **k):
            return

    notifier = _DummyNotifier()


DEFAULT_ACHIEVEMENTS: List[Dict] = [
    # Winning achievements
    {"id": "first_win", "title": "First Win", "desc": "Win your first round.", "unlocked": False},
    {"id": "lucky_strike", "title": "Lucky Strike", "desc": "Win two rounds in a row.", "unlocked": False},
    {"id": "triple_threat", "title": "Triple Threat", "desc": "Win three rounds in a row.", "unlocked": False},
    {"id": "unstoppable", "title": "Unstoppable", "desc": "Win five rounds in a row.", "unlocked": False},
    {"id": "champion", "title": "Champion", "desc": "Win a game (reach 0 chips).", "unlocked": False},
    
    # Rolling achievements
    {"id": "big_roller", "title": "Big Roller", "desc": "Roll a total of 20 or more.", "unlocked": False},
    {"id": "perfect_roll", "title": "Perfect Roll", "desc": "Roll three sixes (666).", "unlocked": False},
    {"id": "zanzibar", "title": "Zanzibar!", "desc": "Roll the legendary 4-5-6.", "unlocked": False},
    {"id": "snake_eyes", "title": "Snake Eyes", "desc": "Roll three ones (111).", "unlocked": False},
    {"id": "unlucky_roll", "title": "Unlucky Roll", "desc": "Roll the cursed 1-2-3.", "unlocked": False},
    {"id": "roll_master", "title": "Roll Master", "desc": "Roll 100 times in a single game.", "unlocked": False},
    {"id": "dice_god", "title": "Dice God", "desc": "Roll 5 straights in one game.", "unlocked": False},
    
    # Shopping achievements
    {"id": "collector", "title": "Collector", "desc": "Buy 10 items from the shop.", "unlocked": False},
    {"id": "shopaholic", "title": "Shopaholic", "desc": "Buy 25 items from the shop.", "unlocked": False},
    {"id": "big_spender", "title": "Big Spender", "desc": "Spend 100 chips in the shop.", "unlocked": False},
    {"id": "window_shopper", "title": "Window Shopper", "desc": "Visit the shop 10 times without buying.", "unlocked": False},
    
    # Inventory/Item achievements
    {"id": "pack_rat", "title": "Pack Rat", "desc": "Hold 10 items in inventory at once.", "unlocked": False},
    {"id": "item_hoarder", "title": "Item Hoarder", "desc": "Accumulate 20 total items (doesn't need to be at once).", "unlocked": False},
    {"id": "item_user", "title": "Item User", "desc": "Use 15 items in a single game.", "unlocked": False},
    {"id": "strategist", "title": "Strategist", "desc": "Use 3 different item types in one game.", "unlocked": False},
    
    # Chip-related achievements
    {"id": "high_roller", "title": "High Roller", "desc": "Reach 50 chips at any point.", "unlocked": False},
    {"id": "chip_baron", "title": "Chip Baron", "desc": "Reach 100 chips at any point.", "unlocked": False},
    {"id": "comeback_kid", "title": "Comeback Kid", "desc": "Win after having 3 or fewer chips.", "unlocked": False},
    {"id": "close_call", "title": "Close Call", "desc": "Win with exactly 1 chip remaining.", "unlocked": False},
    
    # Special hand achievements
    {"id": "triple_master", "title": "Triple Master", "desc": "Roll three of a kind 5 times.", "unlocked": False},
    {"id": "pair_collector", "title": "Pair Collector", "desc": "Roll 10 pairs in one game.", "unlocked": False},
    {"id": "straight_shooter", "title": "Straight Shooter", "desc": "Roll a straight (1-2-3, 2-3-4, 3-4-5, or 4-5-6).", "unlocked": False},
    
    # Participation achievements
    {"id": "veteran", "title": "Veteran", "desc": "Play 10 complete games.", "unlocked": False},
    {"id": "dedicated", "title": "Dedicated", "desc": "Play 50 rounds total.", "unlocked": False},
    {"id": "marathon_player", "title": "Marathon Player", "desc": "Play a game lasting 30+ rounds.", "unlocked": False},
    
    # Social/Fun achievements
    {"id": "party_starter", "title": "Party Starter", "desc": "Start a game with 4+ players.", "unlocked": False},
    {"id": "lone_wolf", "title": "Lone Wolf", "desc": "Play a 2-player game.", "unlocked": False},
    {"id": "generous", "title": "Generous", "desc": "Give away chips to another player (via losing rounds).", "unlocked": False},
    
    # Secret/Easter Egg achievements
    {"id": "achievement_hunter", "title": "Achievement Hunter", "desc": "Unlock 10 achievements.", "unlocked": False},
    {"id": "completionist", "title": "Completionist", "desc": "Unlock all achievements.", "unlocked": False},
    {"id": "early_bird", "title": "Early Bird", "desc": "Win a game in under 10 rounds.", "unlocked": False},
    {"id": "persistence", "title": "Persistence", "desc": "Continue playing after a 10-round losing streak.", "unlocked": False},
]


class AchievementsManager:
    """In-memory achievements manager for the running session.

    This manager does not persist by default (Option A). Use `unlock(id)` to
    mark an achievement unlocked during the session; this will also show the
    popup via the notifier.
    """

    def __init__(self, defaults: List[Dict] = None):
        self._defaults = defaults or DEFAULT_ACHIEVEMENTS
        # store by id for quick lookup
        self._ach: Dict[str, Dict] = {}
        for a in self._defaults:
            self._ach[a['id']] = dict(a)

    def get_all(self) -> List[Dict]:
        """Return a list of achievement dicts (id,title,desc,unlocked)."""
        return [dict(v) for v in self._ach.values()]

    def is_unlocked(self, aid: str) -> bool:
        a = self._ach.get(aid)
        return bool(a and a.get('unlocked'))

    def unlock(self, aid: str) -> bool:
        """Mark achievement unlocked for this session. Returns True when state changed."""
        a = self._ach.get(aid)
        if not a:
            return False
        if a.get('unlocked'):
            return False
        a['unlocked'] = True
        # show a popup via the notifier, with a small procedurally generated
        # pixel-art icon to match the Achievements menu.
        try:
            icon = _get_icon_surface(aid, 64, True)
            notifier.show(a.get('title', 'Achievement'), a.get('desc', ''), image=icon, placement='bottom-right')
        except Exception:
            try:
                notifier.show(a.get('title', 'Achievement'), a.get('desc', ''), placement='bottom-right')
            except Exception:
                pass
        return True

    def reset_session(self):
        """Reset unlocked flags for current session."""
        for a in self._ach.values():
            a['unlocked'] = False


def _get_icon_surface(aid: str, size: int, unlocked: bool) -> 'pygame.Surface':
    """Create a small pixel-art surface for the given achievement id.

    This duplicates the style used in the AchievementsMenu so the popup and
    the menu match visually.
    """
    try:
        import pygame
    except Exception:
        return None

    # Simple palette
    _palette = [
        (220, 80, 60),
        (80, 180, 120),
        (90, 120, 220),
        (200, 140, 220),
        (240, 200, 90),
    ]

    key = (aid, size, bool(unlocked))
    # deterministic pseudo-random from id
    seed = abs(hash(aid))
    color = _palette[seed % len(_palette)] if unlocked else (120, 120, 120)

    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    grid = 6
    cell = size // grid
    for gy in range(grid):
        for gx in range(grid):
            idx = (gx + gy * grid) ^ (seed & 0xFF)
            on = (idx % 3) == 0 or ((gx + gy) % 5 == 0 and (seed >> (gx+gy)) & 1)
            if unlocked:
                on = on or ((idx + seed) % 4 == 0)
            if on:
                rx = gx * cell
                ry = gy * cell
                rect = pygame.Rect(rx, ry, cell + 1, cell + 1)
                pygame.draw.rect(surf, color, rect)
    # border
    try:
        pygame.draw.rect(surf, (40, 40, 40), (0, 0, size, size), 1)
    except Exception:
        pass
    return surf


# module-level singleton used by the app
achievements = AchievementsManager()
