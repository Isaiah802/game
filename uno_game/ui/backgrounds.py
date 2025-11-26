import os
import random
import pygame


class BackgroundRenderer:
    """Reusable background renderer: cover image + tint, fabric texture, animated grain, vignette."""

    def __init__(self, width: int, height: int, felt_color=(12, 80, 34), bg_filename='ui/casino_background.jpg'):
        self.width = width
        self.height = height
        self.felt_color = felt_color
        self._grain_offset = 0.0
        self._grain_speed = 12.0  # pixels per second

        # try load background image from assets folder
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        assets_dir = os.path.join(base, 'assets')
        self.bg_surface = None
        try:
            path = os.path.join(assets_dir, bg_filename)
            if os.path.exists(path):
                self.bg_surface = pygame.image.load(path).convert_alpha()
        except Exception:
            self.bg_surface = None

        # precreate vignette
        self.vignette = self._make_vignette(self.width, self.height, max_alpha=160)

        # precreate small grain surface (tile-able)
        self._grain = self._make_grain(128, 128)

    def _make_vignette(self, width: int, height: int, max_alpha: int = 160) -> pygame.Surface:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        cx = width // 2
        cy = height // 2
        step = max(8, int(max(width, height) / 80))
        for r in range(int(max(width, height)), 0, -step):
            a = int(max_alpha * (r / max(width, height)))
            a = max(0, min(255, a))
            pygame.draw.circle(surf, (0, 0, 0, a), (cx, cy), r)
        return surf

    def _make_grain(self, w: int, h: int) -> pygame.Surface:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for x in range(w):
            for y in range(h):
                v = random.randint(0, 40)
                surf.set_at((x, y), (v, v, v, 18))
        return surf

    def update(self, dt: float) -> None:
        self._grain_offset = (self._grain_offset + self._grain_speed * dt) % self._grain.get_height()

    def draw(self, surface: pygame.Surface, spotlight_surf: pygame.Surface = None, spotlight_center=(0, 0)) -> None:
        w, h = surface.get_size()

        # background image scaled cover
        if self.bg_surface:
            bg = pygame.transform.smoothscale(self.bg_surface, (w, h))
            surface.blit(bg, (0, 0))
            # tint with felt color to keep UI readable
            tint = pygame.Surface((w, h), pygame.SRCALPHA)
            tint.fill((self.felt_color[0], self.felt_color[1], self.felt_color[2], 64))
            surface.blit(tint, (0, 0))
        else:
            surface.fill(self.felt_color)

        # subtle diagonal fabric overlay (cheap)
        tex_s = pygame.Surface((w, h), pygame.SRCALPHA)
        step = 14
        col = (0, 0, 0, 18)
        for x in range(-h, w, step):
            pygame.draw.line(tex_s, col, (x, 0), (x + h, h), 1)
        surface.blit(tex_s, (0, 0))

        # grain tiled with offset
        gx, gy = self._grain.get_size()
        offs = int(self._grain_offset)
        for x in range(0, w, gx):
            for y in range(-gy, h, gy):
                surface.blit(self._grain, (x, y + offs))

        # vignette on top
        if self.vignette:
            surface.blit(self.vignette, (0, 0))

        # optional spotlight (additive) drawn by caller after draw if needed
