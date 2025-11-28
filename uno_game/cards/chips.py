import pygame
import math
from typing import Tuple, Dict

# Simple visual chip drawer for the game UI.
# Each chip is drawn as a circular token with a border. Large counts show a +N label.

DEFAULT_COLORS = [
    (180, 30, 30),   # red
    (30, 90, 30),    # green
    (40, 40, 120),   # blue
    (80, 40, 10),    # brown
    (160, 120, 40),  # gold/yellow
]

_chip_cache: Dict[Tuple[Tuple[int,int,int], int], pygame.Surface] = {}

def _get_fancy_chip(color: Tuple[int,int,int], radius: int) -> pygame.Surface:
    key = (color, radius)
    if key in _chip_cache:
        return _chip_cache[key]

    size = radius*2 + 8
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size//2, size//2
    r = radius

    rim_base = (212, 175, 55)
    rim_dark = (140, 110, 30)
    rim_light = (245, 220, 120)

    # Rim gradient
    for yy in range(-r, r+1):
        for xx in range(-r, r+1):
            dist = (xx*xx + yy*yy)**0.5
            if r-1 <= dist <= r:
                t = (yy + r)/(2*r)
                cr = int(rim_base[0] + (rim_dark[0]-rim_base[0])*t)
                cg = int(rim_base[1] + (rim_dark[1]-rim_base[1])*t)
                cb = int(rim_base[2] + (rim_dark[2]-rim_base[2])*t)
                surf.set_at((cx+xx, cy+yy), (cr, cg, cb, 255))

    # Specular highlight arc
    for ang_deg in range(-40, 41, 3):
        ang = math.radians(ang_deg)
        hx = int(cx + math.cos(ang)*r)
        hy = int(cy - math.sin(ang)*r*0.85)
        if 0 <= hx < size and 0 <= hy < size:
            surf.set_at((hx, hy), rim_light)

    # Stripe segments
    stripe_count = 8
    stripe_w = max(1, r//6)
    stripe_r0 = r-1
    stripe_r1 = r - max(2, r//4)
    for i in range(stripe_count):
        a0 = (2*math.pi*i)/stripe_count
        for rr in range(stripe_r1, stripe_r0+1):
            for sw in range(-stripe_w, stripe_w+1):
                ang = a0 + (sw/(stripe_w*4))
                px = int(cx + math.cos(ang)*rr)
                py = int(cy + math.sin(ang)*rr)
                if 0 <= px < size and 0 <= py < size:
                    surf.set_at((px, py), (245,245,245,255))

    # Inner disk with radial darkening
    inner_r = int(r*0.78)
    for yy in range(-inner_r, inner_r+1):
        for xx in range(-inner_r, inner_r+1):
            dist = (xx*xx + yy*yy)**0.5
            if dist <= inner_r:
                t = dist/inner_r
                darken = 0.35*t
                cr = int(color[0]*(1-darken))
                cg = int(color[1]*(1-darken))
                cb = int(color[2]*(1-darken))
                surf.set_at((cx+xx, cy+yy), (cr,cg,cb,255))

    # Center highlight
    center_r = max(2, int(r*0.22))
    for yy in range(-center_r, center_r+1):
        for xx in range(-center_r, center_r+1):
            if xx*xx + yy*yy <= center_r*center_r:
                surf.set_at((cx+xx, cy+yy), (250,250,250,200))

    # Denomination text (map color to nominal value)
    denom_map = {
        (180,30,30): '50',
        (30,90,30): '25',
        (40,40,120): '100',
        (80,40,10): '5',
        (160,120,40): '10'
    }
    denom = denom_map.get(color)
    if denom:
        try:
            font = pygame.font.SysFont('Arial', max(10, int(r*0.9)), bold=True)
            txt = font.render(denom, True, (30,30,30))
            tr = txt.get_rect(center=(cx, cy))
            surf.blit(txt, tr)
        except Exception:
            pass

    _chip_cache[key] = surf
    return surf


def _choose_color(count: int) -> Tuple[int, int, int]:
    # Choose a color based on magnitude so stacks look varied
    return DEFAULT_COLORS[(count // 5) % len(DEFAULT_COLORS)]


def draw_chip(surface: pygame.Surface, cx: int, cy: int, radius: int, color: Tuple[int, int, int]):
    base = _get_fancy_chip(color, radius)
    rect = base.get_rect(center=(int(cx), int(cy)))
    # drop shadow
    shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shadow, (0,0,0,90), (shadow.get_width()//2 + 2, shadow.get_height()//2 + 4), radius)
    surface.blit(shadow, (rect.x, rect.y))
    surface.blit(base, rect)


def draw_chip_stack(surface: pygame.Surface, x: int, y: int, count: int, *,
                    chip_radius: int = 8, x_spacing: int = 1, y_spacing: int = 4,
                    max_display: int = 12, font: pygame.font.Font | None = None,
                    time_ms: int | None = None):
    """
    Draws a vertical-ish stacked representation of `count` chips with overlap.

    - x, y: top-left position of the stack area (chips are drawn to the right of this)
    - count: number of chips to represent
    - chip_radius: radius of each chip token
    - max_display: maximum number of chip tokens to actually draw; if count > max_display,
      a "+N" label will be shown indicating the remaining chips.
    
    Returns:
        tuple: (rect: pygame.Rect, metadata: dict)
        - rect: the bounding rectangle occupied by the drawn stack
        - metadata: {
            'total': int,
            'denominations': dict mapping color -> count,
            'overflow': int (chips not shown if > max_display)
          }
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

    # Build denominations mapping
    denominations = {}
    denom_values = {
        (180,30,30): 50,   # red
        (30,90,30): 25,    # green
        (40,40,120): 100,  # blue
        (80,40,10): 5,     # brown
        (160,120,40): 10   # gold
    }
    
    # stack upwards (later chips drawn on top)
    # animation phase
    phase = (time_ms / 1000.0) if time_ms is not None else 0.0
    for i in range(max_draw):
        offset = (max_draw - 1 - i) * (chip_radius - y_spacing)
        color = _choose_color(count - i)
        # Count this chip in denominations
        value = denom_values.get(color, 0)
        denominations[value] = denominations.get(value, 0) + 1
        # subtle bob + horizontal sway
        bob = math.sin(phase * 2.7 + i * 0.55) * 1.5
        sway = math.sin(phase * 1.9 + i * 0.33) * 1.2
        draw_chip(surface, cx + sway, cy + offset + bob, chip_radius, color)

    # If there's overflow, draw a label on top
    overflow = count - max_draw
    if overflow > 0:
        # draw a small darker chip on top and number
        top_x = cx
        top_y = cy - (max_draw - 1) * (chip_radius - y_spacing)
        # darker fancy chip without stripes for overflow indicator
        ov = pygame.Surface((chip_radius*2+8, chip_radius*2+8), pygame.SRCALPHA)
        pygame.draw.circle(ov, (40,40,40), (ov.get_width()//2, ov.get_height()//2), chip_radius)
        pygame.draw.circle(ov, (0,0,0), (ov.get_width()//2, ov.get_height()//2), chip_radius, 2)
        surface.blit(ov, (top_x - ov.get_width()//2, top_y - ov.get_height()//2))
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
    rect = pygame.Rect(x, y, int(width), int(max(2 * chip_radius, height)))
    
    metadata = {
        'total': count,
        'denominations': denominations,
        'overflow': overflow
    }
    
    return rect, metadata
