import typing
from typing import Dict, List
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
    {"id": "first_win", "title": "First Win", "desc": "Win your first round.", "unlocked": False},
    {"id": "big_roller", "title": "Big Roller", "desc": "Roll a 20 total.", "unlocked": False},
    {"id": "collector", "title": "Collector", "desc": "Buy 10 items from the shop.", "unlocked": False},
    {"id": "lucky_strike", "title": "Lucky Strike", "desc": "Win two rounds in a row.", "unlocked": False},
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
