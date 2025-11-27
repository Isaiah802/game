import pygame
import random
import math
from typing import Callable, Optional

# small cache for pre-rendered chip surfaces to avoid per-frame drawing
_chip_surface_cache: dict = {}


def _get_chip_surface(color: tuple, radius: float) -> pygame.Surface:
    key = (color, int(radius))
    if key in _chip_surface_cache:
        return _chip_surface_cache[key]
    size = int(radius * 2 + 4)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2)
    rim_color = (212, 175, 55)
    pygame.draw.circle(surf, rim_color, center, int(radius))
    inner_r = max(1, int(radius * 0.82))
    pygame.draw.circle(surf, color, center, inner_r)
    center_r = max(1, int(radius * 0.14))
    pygame.draw.circle(surf, (245, 245, 245, 200), center, center_r)
    _chip_surface_cache[key] = surf
    return surf


def _make_vignette(width: int, height: int, max_alpha: int = 160) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    cx = width // 2
    cy = height // 2
    max_r = max(width, height) // 1
    # draw large circles from outer -> inner so edges are darker
    step = max(8, int(max(width, height) / 80))
    for r in range(int(max(width, height)), 0, -step):
        a = int(max_alpha * (r / max(width, height)))
        a = max(0, min(255, a))
        pygame.draw.circle(surf, (0, 0, 0, a), (cx, cy), r)
    return surf


def _make_spotlight(radius: int, color=(255, 245, 200), max_alpha: int = 220) -> pygame.Surface:
    size = int(radius * 2)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2
    cy = size // 2
    for r in range(radius, 0, -1):
        t = (1.0 - (r / radius))
        a = int(max_alpha * (t * t))
        a = max(0, min(255, a))
        col = (color[0], color[1], color[2], a)
        pygame.draw.circle(surf, col, (cx, cy), r)
    return surf


class Button:
    def __init__(self, rect: pygame.Rect, text: str, callback: Callable[[], None], font: pygame.font.Font, bg=(200, 200, 200), fg=(0, 0, 0)):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.font = font
        self.bg = bg
        self.fg = fg
        self.hovered = False

    def draw(self, surface: pygame.Surface):
        """Draw a pill-style button (ellipse) but keep rect for collisions."""
        draw_rect = self.rect
        rim_color = (212, 175, 55)  # gold rim

        # glow when hovered
        if getattr(self, 'hovered', False):
            glow = pygame.Surface((draw_rect.width + 24, draw_rect.height + 24), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (212, 175, 55, 48), glow.get_rect())
            surface.blit(glow, glow.get_rect(center=draw_rect.center))

        # rim and inner
        pygame.draw.ellipse(surface, rim_color, draw_rect)
        inner = draw_rect.inflate(-8, -8)
        pygame.draw.ellipse(surface, self.bg, inner)

        # label
        txt = self.font.render(self.text, True, self.fg)
        txt_r = txt.get_rect(center=draw_rect.center)
        surface.blit(txt, txt_r)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)


class ChipParticle:
    """Simple falling chip particle.

    Position/velocity in floats. Drawn as a rim + inner colored circle to look like chips.
    """
    def __init__(self, x: float, y: float, vx: float, vy: float, radius: float, color: tuple):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        # keep life simple — we'll fade based on vertical progress
        self.spawn_y = y

    def update(self, dt: float, gravity: float) -> None:
        self.vy += gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        # rotation/spin removed for a cleaner look and cheaper rendering

    def is_offscreen(self, height: int) -> bool:
        return self.y - self.radius > height

    def draw(self, surface: pygame.Surface) -> None:
        # use pre-rendered surface and apply fade alpha
        surf = _get_chip_surface(self.color, self.radius)
        # compute alpha: fade as the chip travels down the screen
        # keep a minimum alpha so chips are visible
        alpha = int(max(60, min(255, 255 * (1.0 - (self.y / (surface.get_height() + 100.0))))))
        s = surf.copy()
        s.set_alpha(alpha)
        rect = s.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(s, rect)


class DiceParticle:
    """Lightweight pseudo-3D dice particle.

    Draws a front face and a top face polygon to simulate a 3D cube. No real rotation is applied
    (keeps rendering cheap), but dice have a small angle for a tiny wobble effect.
    """
    def __init__(self, x: float, y: float, vx: float, vy: float, size: float, value: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.value = max(1, min(6, int(value)))
        self.wobble = random.uniform(-30.0, 30.0)
        self.wobble_speed = random.uniform(-40.0, 40.0)
        self.spawn_y = y

    def update(self, dt: float, gravity: float) -> None:
        self.vy += gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.wobble = (self.wobble + self.wobble_speed * dt) % 360.0

    def is_offscreen(self, height: int) -> bool:
        return self.y - self.size > height

    def draw(self, surface: pygame.Surface) -> None:
        # pseudo-3D cube: front rect and a top polygon shifted up-left
        s = int(max(6, self.size))
        x = int(self.x)
        y = int(self.y)
        # base colors
        face_color = (240, 240, 240)
        top_color = (220, 220, 220)
        pip_color = (20, 20, 20)

        # front rect
        front_rect = pygame.Rect(x - s // 2, y - s // 2 + int(s * 0.12), s, s)
        pygame.draw.rect(surface, face_color, front_rect, border_radius=max(2, s//6))

        # top face polygon
        offset = int(s * 0.18)
        top_poly = [
            (x - s // 2, y - s // 2 + int(s * 0.12)),
            (x - s // 2 + offset, y - s // 2 - offset + int(s * 0.12)),
            (x + s // 2 + offset, y - s // 2 - offset + int(s * 0.12)),
            (x + s // 2, y - s // 2 + int(s * 0.12)),
        ]
        pygame.draw.polygon(surface, top_color, top_poly)

        # a subtle rim
        rim_rect = front_rect.inflate(2, 2)
        pygame.draw.rect(surface, (200, 200, 200), rim_rect, width=1, border_radius=max(2, s//6))

        # draw simple pips for values 1-6 (arranged roughly)
        pip_positions = {
            1: [(0, 0)],
            2: [(-0.25, -0.25), (0.25, 0.25)],
            3: [(-0.3, -0.3), (0, 0), (0.3, 0.3)],
            4: [(-0.3, -0.3), (-0.3, 0.3), (0.3, -0.3), (0.3, 0.3)],
            5: [(-0.3, -0.3), (-0.3, 0.3), (0, 0), (0.3, -0.3), (0.3, 0.3)],
            6: [(-0.3, -0.45), (-0.3, 0), (-0.3, 0.45), (0.3, -0.45), (0.3, 0), (0.3, 0.45)],
        }
        positions = pip_positions.get(self.value, pip_positions[1])
        pip_r = max(1, s // 10)
        for px, py in positions:
            px_c = int(x + px * s)
            py_c = int(y + py * s + int(s * 0.12))
            pygame.draw.circle(surface, pip_color, (px_c, py_c), pip_r)


class StartMenu:
    """Simple Start Menu UI using pygame.

    Usage:
        menu = StartMenu(screen)
        choice = menu.run()  # returns one of: 'play', 'settings', 'change_song', 'keybindings', 'achievements', 'quit'
    """

    def __init__(self, screen: pygame.Surface, width=800, height=600):
        self.screen = screen
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 28)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.result: Optional[str] = None

        # minimal casino styling
        self.felt_color = (12, 80, 34)
        self.title_text = "A simple Zanzibar Game"

    # Buttons will be created in build_ui

        # Mini "lego" style avatar (initialize BEFORE build_ui so build_ui can reference it)
        self.avatar_enabled = True
        self.avatar_rect = pygame.Rect(0, 0, 1, 1)  # placeholder until buttons built
        self.avatar_hover = False
        self.rule_snippets = [
            "Roll 5 dice.",
            "Hands rank high to low.",
            "Straights beat triples.",
            "Reach 0 chips to win.",
            "Items can alter rolls.",
        ]
        self.current_rule_index = 0
        self.rule_cycle_timer = 0.0
        self.rule_cycle_interval = 5.0

        # Buttons will be created in build_ui
        self.buttons = []
        self.build_ui()
        # particle system for falling chips (tunable, cleaner defaults)
        self.chips_enabled = True
        self.particles = []  # list[ChipParticle]
        self.spawn_timer = 0.0
        self.spawn_interval = 0.22  # seconds between small bursts (slower)
        self.gravity = 600.0  # px/s^2
        self.max_particles = 64  # lower cap for a cleaner look
        # chip palette (kept small)
        self.chip_colors = [
            (180, 30, 30),
            (30, 90, 30),
            (40, 40, 120),
            (80, 40, 10),
        ]
        # dice particle system (pseudo-3D)
        self.dice_enabled = True
        self.dice_particles = []  # list[DiceParticle]
        self.dice_spawn_timer = 0.0
        self.dice_spawn_interval = 1.25  # spawn a die every ~1.25s
        self.max_dice = 6
        # vignette (clean focus)
        self.vignette_surf = _make_vignette(self.width, self.height)
        self.spotlight_enabled = False  # Spotlight disabled for cleaner look

        # (avatar vars already initialized above prior to build_ui)

    def build_ui(self):
        btn_w, btn_h = 360, 64
        start_x = (self.width - btn_w) // 2
        start_y = 200
        gap = 20

        def make_btn(i, text, key):
            r = pygame.Rect(start_x, start_y + i * (btn_h + gap), btn_w, btn_h)

            def cb():
                self.result = key

            # chip-ish inner color per button
            color_map = {
                0: (180, 30, 30),  # Play - red
                1: (30, 90, 30),   # Audio - green
                2: (40, 40, 120),  # Change Song - navy
                3: (80, 40, 10),   # Keybindings - brownish
                4: (120, 60, 180), # Achievements - purple
                5: (40, 40, 40),   # Quit - dark
            }
            bgc = color_map.get(i, (240, 240, 240))
            return Button(rect=r, text=text, callback=cb, font=self.font, bg=bgc, fg=(245, 245, 245))

        self.buttons = [
            make_btn(0, "Play", 'play'),
            make_btn(1, "Audio Settings", 'settings'),
            make_btn(2, "Change Song", 'change_song'),
            make_btn(3, "Keybindings", 'keybindings'),
            make_btn(4, "Achievements", 'achievements'),
            make_btn(5, "Quit", 'quit'),
        ]
        # keyboard selection index
        self.selected = 0
        # initialize hovered state
        for i, b in enumerate(self.buttons):
            b.hovered = (i == self.selected)
        # After buttons are available, define a tiny avatar positioned just to the right of the Quit button
        if self.avatar_enabled and self.buttons:
            quit_rect = self.buttons[-1].rect
            # Larger avatar dimensions for better detail (curly hair etc.)
            av_w, av_h = 100, 160
            gap = 12
            x = quit_rect.right + gap
            y = quit_rect.centery - av_h // 2
            # Clamp inside window
            if x + av_w > self.width - 8:
                x = self.width - av_w - 8
            if y < 8:
                y = 8
            if y + av_h > self.height - 8:
                y = self.height - av_h - 8
            self.avatar_rect = pygame.Rect(x, y, av_w, av_h)

    def draw(self):
        # felt background
        self.screen.fill(self.felt_color)

        # subtle fabric texture: thin diagonal lines
        tex_color = (0, 0, 0, 18)
        tex_s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        step = 14
        for x in range(-self.height, self.width, step):
            pygame.draw.line(tex_s, tex_color, (x, 0), (x + self.height, self.height), 1)
        self.screen.blit(tex_s, (0, 0))

        # vignette (darken edges)
        if self.vignette_surf:
            self.screen.blit(self.vignette_surf, (0, 0))

        # falling chips and dice (behind UI elements)
        if self.chips_enabled:
            for p in self.particles:
                p.draw(self.screen)
        if self.dice_enabled:
            for d in self.dice_particles:
                d.draw(self.screen)

        # spotlight (soft additive glow near title)
        if self.spotlight_enabled and self.spotlight_surf is not None:
            sp = self.spotlight_surf
            rect = sp.get_rect(center=(int(self.spotlight_center[0]), int(self.spotlight_center[1])))
            try:
                self.screen.blit(sp, rect, special_flags=pygame.BLEND_RGBA_ADD)
            except Exception:
                # fallback to normal blit if blend flag unsupported
                self.screen.blit(sp, rect)

        # title with shadow and gold stroke (top)
        title_text = self.title_text
        # shadow
        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_r = shadow.get_rect(center=(self.width // 2, 60))
        shadow_pos = (shadow_r.x + 4, shadow_r.y + 4)
        self.screen.blit(shadow, shadow_pos)

        # gold stroke
        gold = (212, 175, 55)
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            t = self.title_font.render(title_text, True, gold)
            tr = t.get_rect(center=(self.width // 2 + ox, 60 + oy))
            self.screen.blit(t, tr)

        # main title
        title = self.title_font.render(title_text, True, (245, 245, 245))
        tr = title.get_rect(center=(self.width // 2, 60))
        self.screen.blit(title, tr)

        # draw buttons
        for b in self.buttons:
            b.draw(self.screen)

        # Draw mini avatar beside Quit button (lego style with hoodie)
        if self.avatar_enabled:
            ar = self.avatar_rect
            panel = pygame.Surface(ar.size, pygame.SRCALPHA)
            panel.fill((0, 0, 0, 70))
            self.screen.blit(panel, ar.topleft)

            # Geometry
            head_r = max(6, ar.width // 4)
            head_x = ar.x + ar.width // 2
            head_y = ar.y + head_r + 4
            body_w = int(ar.width * 0.8)
            body_h = int(ar.height * 0.30)
            body_x = head_x - body_w // 2
            body_y = head_y + head_r - 2
            leg_w = int(body_w * 0.42)
            leg_h = max(8, int(ar.height * 0.32))
            leg_gap = max(2, int(body_w * 0.08))
            leg1_x = head_x - leg_w - leg_gap//2
            leg2_x = head_x + leg_gap//2
            leg_y = body_y + body_h - 2
            arm_w = max(4, int(body_w * 0.18))
            arm_h = int(body_h * 0.9)
            arm1_x = body_x - arm_w + 2
            arm2_x = body_x + body_w - 2
            arm_y = body_y + 2

            # Colors
            skin = (255, 230, 180)
            hoodie = (90, 0, 30)
            hoodie_outline = (50, 0, 15)
            pants = (30, 30, 40)
            outline = (20, 20, 20)
            hair_color = (245, 220, 100)
            beard_color = (180, 140, 80)

            # Head + hair
            pygame.draw.circle(self.screen, skin, (head_x, head_y), head_r)
            pygame.draw.circle(self.screen, outline, (head_x, head_y), head_r, 1)
            # Full straight hair (no curls): layered top + side coverage
            # Top oval
            top_h = head_r + 6
            top_rect = pygame.Rect(head_x - head_r - 2, head_y - head_r - 4, head_r * 2 + 4, top_h)
            pygame.draw.ellipse(self.screen, hair_color, top_rect)
            pygame.draw.ellipse(self.screen, (200,170,70), top_rect, 1)
            # Lower hair band to ensure full coverage around forehead
            band_h = head_r // 2 + 2
            band_rect = pygame.Rect(head_x - head_r + 2, head_y - head_r//2, head_r * 2 - 4, band_h)
            pygame.draw.rect(self.screen, hair_color, band_rect, border_radius=band_h//2)
            pygame.draw.rect(self.screen, (200,170,70), band_rect, 1, border_radius=band_h//2)

            # Face (eyes)
            eye_r = max(1, head_r // 5)
            eye_y = head_y - eye_r
            pygame.draw.circle(self.screen, (0,0,0), (head_x - eye_r*2, eye_y), eye_r)
            pygame.draw.circle(self.screen, (0,0,0), (head_x + eye_r*2, eye_y), eye_r)

            # Beard + mouth
            beard_height = head_r // 2 + 2
            beard_rect = pygame.Rect(head_x - head_r + 3, head_y - 2, head_r*2 - 6, beard_height)
            pygame.draw.rect(self.screen, beard_color, beard_rect, border_radius=head_r//2)
            mouth_skin_r = max(3, head_r // 3)
            pygame.draw.circle(self.screen, skin, (head_x, head_y + head_r//4), mouth_skin_r)
            mouth_rect = pygame.Rect(head_x - mouth_skin_r, head_y + head_r//4 - mouth_skin_r//2, mouth_skin_r*2, mouth_skin_r)
            pygame.draw.arc(self.screen, (0,0,0), mouth_rect, math.pi*0.15, math.pi - math.pi*0.15, 1)

            # Hoodie torso
            pygame.draw.rect(self.screen, hoodie, (body_x, body_y, body_w, body_h), border_radius=4)
            pygame.draw.rect(self.screen, hoodie_outline, (body_x, body_y, body_w, body_h), 1, border_radius=4)
            pocket_w = int(body_w * 0.55)
            pocket_h = int(body_h * 0.32)
            pocket_x = head_x - pocket_w // 2
            pocket_y = body_y + body_h - pocket_h - 4
            pygame.draw.rect(self.screen, (110, 20, 40), (pocket_x, pocket_y, pocket_w, pocket_h), border_radius=3)
            pygame.draw.rect(self.screen, (70, 10, 25), (pocket_x, pocket_y, pocket_w, pocket_h), 1, border_radius=3)
            logo_font = pygame.font.SysFont('Arial', max(10, head_r))
            logo = logo_font.render('A&M', True, (245,245,245))
            logo_rect = logo.get_rect(center=(head_x, body_y + body_h * 0.35))
            if logo_rect.width < body_w - 4:
                self.screen.blit(logo, logo_rect)

            # Arms
            pygame.draw.rect(self.screen, skin, (arm1_x, arm_y, arm_w, arm_h), border_radius=3)
            pygame.draw.rect(self.screen, outline, (arm1_x, arm_y, arm_w, arm_h), 1, border_radius=3)
            pygame.draw.rect(self.screen, skin, (arm2_x, arm_y, arm_w, arm_h), border_radius=3)
            pygame.draw.rect(self.screen, outline, (arm2_x, arm_y, arm_w, arm_h), 1, border_radius=3)

            # Legs
            pygame.draw.rect(self.screen, pants, (leg1_x, leg_y, leg_w, leg_h), border_radius=3)
            pygame.draw.rect(self.screen, outline, (leg1_x, leg_y, leg_w, leg_h), 1, border_radius=3)
            pygame.draw.rect(self.screen, pants, (leg2_x, leg_y, leg_w, leg_h), border_radius=3)
            pygame.draw.rect(self.screen, outline, (leg2_x, leg_y, leg_w, leg_h), 1, border_radius=3)

            # Hover glow + tooltip
            if self.avatar_hover:
                glow = pygame.Surface((ar.width+6, ar.height+6), pygame.SRCALPHA)
                pygame.draw.rect(glow, (212,175,55,80), glow.get_rect(), border_radius=6)
                self.screen.blit(glow, (ar.x-3, ar.y-3))
                snippet = self.rule_snippets[self.current_rule_index]
                tip_font = pygame.font.SysFont('Arial', 18)
                tip_surf = tip_font.render(snippet, True, (245,245,245))
                pad = 6
                tip_w = tip_surf.get_width() + pad*2
                tip_h = tip_surf.get_height() + pad*2
                tip_x = ar.right + 10
                tip_y = ar.y
                if tip_x + tip_w > self.width - 6:
                    tip_x = ar.x
                    tip_y = ar.y - tip_h - 6
                    if tip_y < 0:
                        tip_y = ar.y + ar.height + 6
                box = pygame.Surface((tip_w, tip_h), pygame.SRCALPHA)
                box.fill((0,0,0,170))
                pygame.draw.rect(box, (212,175,55), box.get_rect(), 1, border_radius=6)
                self.screen.blit(box, (tip_x, tip_y))
                self.screen.blit(tip_surf, (tip_x + pad, tip_y + pad))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.result = 'quit'
            for b in self.buttons:
                b.handle_event(event)
            # keyboard navigation
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.buttons)
                    for i, b in enumerate(self.buttons):
                        b.hovered = (i == self.selected)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.buttons)
                    for i, b in enumerate(self.buttons):
                        b.hovered = (i == self.selected)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # trigger the selected button
                    self.buttons[self.selected].callback()
            # avatar hover & click
            if self.avatar_enabled:
                if event.type == pygame.MOUSEMOTION:
                    self.avatar_hover = self.avatar_rect.collidepoint(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.avatar_rect.collidepoint(event.pos):
                        # advance rule snippet on click
                        self.current_rule_index = (self.current_rule_index + 1) % len(self.rule_snippets)

    def run(self) -> str:
        """Run the menu loop until the user chooses an option; returns the choice key."""
        self.result = None
        while self.result is None:
            # tick first to get a consistent dt
            ms = self.clock.tick(60)
            dt = ms / 1000.0
            self.handle_events()
            # update particle simulations
            if self.chips_enabled:
                self.update_particles(dt)
            if self.dice_enabled:
                self.update_dice(dt)
            if self.spotlight_enabled:
                self.update_spotlight(dt)
            # cycle rule snippet while hovered
            if self.avatar_enabled and self.avatar_hover:
                self.rule_cycle_timer += dt
                if self.rule_cycle_timer >= self.rule_cycle_interval:
                    self.rule_cycle_timer = 0.0
                    self.current_rule_index = (self.current_rule_index + 1) % len(self.rule_snippets)
            self.draw()
        return self.result

    def update_particles(self, dt: float) -> None:
        # spawn chips in small bursts
        self.spawn_timer -= dt
        if self.spawn_timer <= 0.0:
            self.spawn_timer += self.spawn_interval
            for _ in range(random.randint(1, 2)):
                if len(self.particles) >= self.max_particles:
                    break
                # spawn in a narrower band to avoid visual clutter at edges
                x = random.uniform(self.width * 0.32, self.width * 0.68)
                y = -20.0
                vx = random.uniform(-40.0, 40.0)
                vy = random.uniform(80.0, 140.0)
                r = random.uniform(10.0, 18.0)
                color = random.choice(self.chip_colors)
                self.particles.append(ChipParticle(x, y, vx, vy, r, color))

        # update and cull
        alive = []
        for p in self.particles:
            p.update(dt, self.gravity)
            if not p.is_offscreen(self.height + 60):
                alive.append(p)
        self.particles = alive

    def update_dice(self, dt: float) -> None:
        # spawn dice occasionally
        self.dice_spawn_timer -= dt
        if self.dice_spawn_timer <= 0.0:
            self.dice_spawn_timer += self.dice_spawn_interval
            if len(self.dice_particles) < self.max_dice and random.random() < 0.9:
                x = random.uniform(self.width * 0.25, self.width * 0.75)
                y = -40.0
                vx = random.uniform(-40.0, 40.0)
                vy = random.uniform(100.0, 180.0)
                size = random.uniform(18.0, 36.0)
                value = random.randint(1, 6)
                self.dice_particles.append(DiceParticle(x, y, vx, vy, size, value))

        alive = []
        for d in self.dice_particles:
            d.update(dt, self.gravity)
            if not d.is_offscreen(self.height + 80):
                alive.append(d)
        self.dice_particles = alive

    def update_spotlight(self, dt: float) -> None:
        # slowly drift the spotlight in a circular-ish path
        self.spotlight_angle += dt * self.spotlight_speed
        base_x = self.width // 2
        base_y = 60
        cx = base_x + math.cos(self.spotlight_angle) * self.spotlight_drift_radius
        cy = base_y + math.sin(self.spotlight_angle * 0.6) * (self.spotlight_drift_radius * 0.25)

        # slight mouse influence to make it feel responsive
        try:
            mx, my = pygame.mouse.get_pos()
        except Exception:
            mx, my = cx, cy
        target_x = cx + (mx - cx) * self.spotlight_mouse_influence
        target_y = cy + (my - cy) * self.spotlight_mouse_influence

        # smooth towards the target
        self.spotlight_center[0] += (target_x - self.spotlight_center[0]) * min(1.0, dt * 3.0)
        self.spotlight_center[1] += (target_y - self.spotlight_center[1]) * min(1.0, dt * 3.0)
