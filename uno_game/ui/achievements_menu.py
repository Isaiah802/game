import pygame
from typing import List, Dict


class AchievementsMenu:
    """Simple achievements viewer stub.

    Usage: Instantiate with screen and call .draw() each frame. Use .handle_event(event)
    which returns True to close the menu.
    """

    def __init__(self, screen: pygame.Surface, achievements: List[Dict] = None):
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 22)
        self.title_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.width = min(760, self.screen.get_width() - 60)
        self.height = min(520, self.screen.get_height() - 60)
        # Load achievements from the session manager if available. This makes
        # the menu reflect unlocks earned during this run (Option A).
        if achievements is None:
            try:
                from achievements import achievements as achievements_manager
                self.achievements = achievements_manager.get_all()
            except Exception:
                # fallback to defaults (locked)
                self.achievements = [
                    {"id": "first_win", "title": "First Win", "desc": "Win your first round.", "unlocked": False},
                    {"id": "big_roller", "title": "Big Roller", "desc": "Roll a 20 total.", "unlocked": False},
                    {"id": "collector", "title": "Collector", "desc": "Buy 10 items from the shop.", "unlocked": False},
                    {"id": "lucky_strike", "title": "Lucky Strike", "desc": "Win two rounds in a row.", "unlocked": False},
                ]
        else:
            # If an explicit list was supplied, respect its unlocked flags.
            self.achievements = [dict(a) for a in achievements]

        # layout
        self.x = (self.screen.get_width() - self.width) // 2
        self.y = (self.screen.get_height() - self.height) // 2
        self.bg_color = (18, 18, 22)
        self.border_color = (100, 100, 120)
        # icon cache
        self._icon_cache = {}
        # palette for unlocked icons
        self._palette = [
            (220, 80, 60),
            (80, 180, 120),
            (90, 120, 220),
            (200, 140, 220),
            (240, 200, 90),
        ]

    def draw_item(self, item, pos_y):
        # small pixel-art icon (colored when unlocked, gray when locked)
        icon_size = 36
        cx = self.x + 24
        cy = pos_y + 18
        icon = self._get_icon_surface(item.get('id', 'unknown'), icon_size, item.get('unlocked', False))
        icon_r = icon.get_rect(center=(cx, cy))
        self.screen.blit(icon, icon_r)

        # title + desc
        t = self.font.render(item.get('title', 'Untitled'), True, (240, 240, 240))
        self.screen.blit(t, (cx + 26, pos_y + 4))
        d = self.font.render(item.get('desc', ''), True, (180, 180, 180))
        self.screen.blit(d, (cx + 26, pos_y + 26))

    def _get_icon_surface(self, aid: str, size: int, unlocked: bool) -> pygame.Surface:
        key = (aid, size, bool(unlocked))
        if key in self._icon_cache:
            return self._icon_cache[key]

        # deterministic pseudo-random pattern based on id
        h = abs(hash(aid))
        seed = h
        # choose a palette color for unlocked
        color = self._palette[seed % len(self._palette)] if unlocked else (120, 120, 120)

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # pixel grid: make a low-res grid and scale up
        grid = 6  # 6x6 grid
        cell = size // grid
        for gy in range(grid):
            for gx in range(grid):
                # symmetric pattern horizontally for nicer icons
                idx = (gx + gy * grid) ^ (seed & 0xFF)
                on = (idx % 3) == 0 or ((gx + gy) % 5 == 0 and (seed >> (gx+gy)) & 1)
                # add more chance if unlocked
                if unlocked:
                    on = on or ((idx + seed) % 4 == 0)
                if on:
                    rx = gx * cell
                    ry = gy * cell
                    rect = pygame.Rect(rx, ry, cell + 1, cell + 1)
                    pygame.draw.rect(surf, color, rect)

        # add a subtle border for visibility
        pygame.draw.rect(surf, (40, 40, 40), (0, 0, size, size), 1)
        self._icon_cache[key] = surf
        return surf

    def draw(self):
        # panel
        pygame.draw.rect(self.screen, self.bg_color, (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(self.screen, self.border_color, (self.x, self.y, self.width, self.height), 2, border_radius=8)

        # title
        title = self.title_font.render("Achievements", True, (230, 230, 230))
        self.screen.blit(title, (self.x + 20, self.y + 12))

        # instructions / back hint
        hint = self.font.render("Press Esc or Backspace to return", True, (180, 180, 180))
        self.screen.blit(hint, (self.x + 20, self.y + 48))

        # list
        start_y = self.y + 90
        gap = 64
        for idx, item in enumerate(self.achievements):
            self.draw_item(item, start_y + idx * gap)

        # draw a simple back button
        btn_w = 120
        btn_h = 40
        bx = self.x + self.width - btn_w - 20
        by = self.y + self.height - btn_h - 20
        btn_rect = pygame.Rect(bx, by, btn_w, btn_h)
        pygame.draw.rect(self.screen, (212, 175, 55), btn_rect, border_radius=8)
        inner = btn_rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, (40, 40, 40), inner, border_radius=6)
        txt = self.font.render("Back", True, (245, 245, 245))
        tr = txt.get_rect(center=btn_rect.center)
        self.screen.blit(txt, tr)
        # store rect for click handling
        self._back_rect = btn_rect

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True when this menu should close."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self, '_back_rect') and self._back_rect.collidepoint(event.pos):
                return True
        return False
