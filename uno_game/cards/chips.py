import pygame
from typing import Tuple

# Simple visual chip drawer for the game UI.
# Each chip is drawn as a circular token with a border. Large counts show a +N label.

DEFAULT_COLORS = [
    (220, 40, 40),   # red
    (40, 180, 60),   # green
    (50, 120, 220),  # blue
    (230, 200, 40),  # yellow
    (180, 100, 30),  # brown/orange
]


def _choose_color(count: int) -> Tuple[int, int, int]:
    # Choose a color based on magnitude so stacks look varied
    return DEFAULT_COLORS[(count // 5) % len(DEFAULT_COLORS)]


def draw_chip(surface: pygame.Surface, cx: int, cy: int, radius: int, color: Tuple[int, int, int]):
    pygame.draw.circle(surface, color, (int(cx), int(cy)), radius)
    pygame.draw.circle(surface, (0, 0, 0), (int(cx), int(cy)), radius, 2)


def draw_chip_stack(surface: pygame.Surface, x: int, y: int, count: int, *,
                    chip_radius: int = 8, x_spacing: int = 1, y_spacing: int = 4,
                    max_display: int = 12, font: pygame.font.Font | None = None):
    """
    Draws a vertical-ish stacked representation of `count` chips with overlap.

    - x, y: top-left position of the stack area (chips are drawn to the right of this)
    - count: number of chips to represent
    - chip_radius: radius of each chip token
    - max_display: maximum number of chip tokens to actually draw; if count > max_display,
      a "+N" label will be shown indicating the remaining chips.
    Returns the rect occupied by the drawn stack.
    """
    if font is None:
        try:
            font = pygame.font.SysFont('Arial', 14)
        except Exception:
            font = None

    # compute layout
    max_draw = min(count, max_display)
    # draw chips slightly staggered to look like a real stack
    cx = x + chip_radius
    cy = y + chip_radius

    # stack upwards (later chips drawn on top)
    for i in range(max_draw):
        offset = (max_draw - 1 - i) * (chip_radius - y_spacing)
        color = _choose_color(count - i)
        draw_chip(surface, cx, cy + offset, chip_radius, color)

    # If there's overflow, draw a label on top
    overflow = count - max_draw
    if overflow > 0:
        # draw a small darker chip on top and number
        top_x = cx
        top_y = cy - (max_draw - 1) * (chip_radius - y_spacing)
        pygame.draw.circle(surface, (40, 40, 40), (int(top_x), int(top_y)), chip_radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(top_x), int(top_y)), chip_radius, 2)
        if font:
            lab = font.render(f'+{overflow}', True, (255, 255, 255))
            lr = lab.get_rect(center=(top_x, top_y))
            surface.blit(lab, lr)

    # render numeric count to the right of stack for clarity
    if font:
        txt = font.render(str(count), True, (230, 230, 230))
        surface.blit(txt, (x + chip_radius * 2 + 6, y))

    text_w = font.size(str(count))[0] if font else 24
    width = chip_radius * 2 + 6 + text_w
    height = chip_radius * 2 + (max_draw - 1) * (chip_radius - y_spacing)
    return pygame.Rect(x, y, int(width), int(max(2 * chip_radius, height)))
