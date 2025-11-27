import pygame
import random
import math
from typing import Callable, Optional

# Ensure this matches your file name for the sprite code
from .Isaiah_npc import IsaiahNPCPixelArt

# ---------------------------------------------------------
#               FRIEND'S CODE & HELPERS
# ---------------------------------------------------------

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
    step = max(8, int(max(width, height) / 80))
    for r in range(int(max(width, height)), 0, -step):
        a = int(max_alpha * (r / max(width, height)))
        a = max(0, min(255, a))
        pygame.draw.circle(surf, (0, 0, 0, a), (cx, cy), r)
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

    def draw(self, surface: pygame.Surface, alpha_mult=1.0):
        draw_rect = self.rect
        rim_color = (212, 175, 55) 

        btn_surf = pygame.Surface((draw_rect.width + 30, draw_rect.height + 30), pygame.SRCALPHA)
        local_rect = pygame.Rect(15, 15, draw_rect.width, draw_rect.height)

        if self.hovered:
            glow_rect = local_rect.inflate(10, 10)
            pygame.draw.ellipse(btn_surf, (212, 175, 55, int(100 * alpha_mult)), glow_rect)

        pygame.draw.ellipse(btn_surf, rim_color, local_rect)
        inner = local_rect.inflate(-8, -8)
        pygame.draw.ellipse(btn_surf, self.bg, inner)

        txt = self.font.render(self.text, True, self.fg)
        txt_r = txt.get_rect(center=local_rect.center)
        btn_surf.blit(txt, txt_r)

        if alpha_mult < 1.0:
            temp = pygame.Surface(btn_surf.get_size(), pygame.SRCALPHA)
            temp.blit(btn_surf, (0, 0))
            temp.set_alpha(int(255 * alpha_mult))
            surface.blit(temp, (draw_rect.x - 15, draw_rect.y - 15))
        else:
            surface.blit(btn_surf, (draw_rect.x - 15, draw_rect.y - 15))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

class ChipParticle:
    def __init__(self, x: float, y: float, vx: float, vy: float, radius: float, color: tuple):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.radius, self.color = radius, color

    def update(self, dt: float, gravity: float) -> None:
        self.vy += gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def is_offscreen(self, height: int) -> bool:
        return self.y - self.radius > height

    def draw(self, surface: pygame.Surface) -> None:
        surf = _get_chip_surface(self.color, self.radius)
        alpha = int(max(60, min(255, 255 * (1.0 - (self.y / (surface.get_height() + 100.0))))))
        s = surf.copy()
        s.set_alpha(alpha)
        rect = s.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(s, rect)

class DiceParticle:
    def __init__(self, x: float, y: float, vx: float, vy: float, size: float, value: int):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.size, self.value = size, max(1, min(6, int(value)))
        self.wobble = random.uniform(-30.0, 30.0)
        self.wobble_speed = random.uniform(-40.0, 40.0)

    def update(self, dt: float, gravity: float) -> None:
        self.vy += gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.wobble = (self.wobble + self.wobble_speed * dt) % 360.0

    def is_offscreen(self, height: int) -> bool:
        return self.y - self.size > height

    def draw(self, surface: pygame.Surface) -> None:
        s = int(max(6, self.size))
        x, y = int(self.x), int(self.y)
        face_color = (240, 240, 240)
        top_color = (220, 220, 220)
        pip_color = (20, 20, 20)

        front_rect = pygame.Rect(x - s // 2, y - s // 2 + int(s * 0.12), s, s)
        pygame.draw.rect(surface, face_color, front_rect, border_radius=max(2, s//6))

        offset = int(s * 0.18)
        top_poly = [
            (x - s // 2, y - s // 2 + int(s * 0.12)),
            (x - s // 2 + offset, y - s // 2 - offset + int(s * 0.12)),
            (x + s // 2 + offset, y - s // 2 - offset + int(s * 0.12)),
            (x + s // 2, y - s // 2 + int(s * 0.12)),
        ]
        pygame.draw.polygon(surface, top_color, top_poly)
        rim_rect = front_rect.inflate(2, 2)
        pygame.draw.rect(surface, (200, 200, 200), rim_rect, width=1, border_radius=max(2, s//6))

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

# ---------------------------------------------------------
#                   START MENU CLASS
# ---------------------------------------------------------

class StartMenu:
    def __init__(self, screen: pygame.Surface, width=800, height=600):
        self.screen = screen
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 28)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.result: Optional[str] = None

        self.felt_color = (12, 80, 34)
        self.title_text = "A simple Zanzibar Game"

        # --- Avatar Logic ---
        self.avatar_enabled = True
        self.avatar_rect = pygame.Rect(0, 0, 1, 1) 
        self.avatar_hover = False
        self.rule_snippets = [
            "Roll 5 dice.", "Hands rank high to low.", "Straights beat triples.",
            "Reach 0 chips to win.", "Items can alter rolls.",
        ]
        self.current_rule_index = 0
        self.rule_cycle_timer = 0.0
        self.rule_cycle_interval = 5.0

        # --- Isaiah NPC Logic ---
        self.Isaiah_npc_hints = [
            "Hi, I'm Isaiah!",              
            "Watch me slice these fruits!", 
            "Watch your chips carefully.",  
            "Use items wisely to win.",     
        ]
        self.Isaiah_npc_index = 0
        self.Isaiah_npc_hover = False
        
        # Animation Mapping
        self.hint_animation_map = {
            0: 'wave', 
            1: 'fruit_combo', 
            2: 'walk',
            3: 'blink'
        }
        self.hint_indices = list(range(len(self.Isaiah_npc_hints)))
        random.shuffle(self.hint_indices)
        self.hint_cycle_pos = 0

        # --- NEW: Idle & Konami Logic ---
        self.idle_timer = 0.0
        self.show_idle_hint = False
        self.idle_hint_shown_once = False 
        
        # Konami Code: Up, Up, Down, Down, Left, Right, Left, Right, b, a (NO ENTER)
        self.konami_code = [
            pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT,
            pygame.K_b, pygame.K_a
        ]
        self.input_buffer = []

        # Buttons
        self.buttons = []
        self.build_ui()
        
        # Particles
        self.chips_enabled = True
        self.particles = []  
        self.spawn_timer = 0.0
        self.spawn_interval = 0.22 
        self.gravity = 600.0 
        self.max_particles = 64 
        self.chip_colors = [(180, 30, 30), (30, 90, 30), (40, 40, 120), (80, 40, 10)]
        self.dice_enabled = True
        self.dice_particles = [] 
        self.dice_spawn_timer = 0.0
        self.dice_spawn_interval = 1.25 
        self.max_dice = 6
        self.vignette_surf = _make_vignette(self.width, self.height)

    def build_ui(self):
        btn_w, btn_h = 360, 64
        start_x = (self.width - btn_w) // 2
        start_y = 200
        gap = 20

        def make_btn(i, text, key):
            r = pygame.Rect(start_x, start_y + i * (btn_h + gap), btn_w, btn_h)
            def cb(): self.result = key
            color_map = {
                0: (180, 30, 30), 1: (30, 90, 30), 2: (40, 40, 120),
                3: (80, 40, 10), 4: (120, 60, 180), 5: (40, 40, 40),
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
        self.selected = 0
        for i, b in enumerate(self.buttons):
            b.hovered = (i == self.selected)
            
        # Avatar Positioning
        if self.avatar_enabled and self.buttons:
            quit_rect = self.buttons[-1].rect
            av_w, av_h = 100, 160
            gap = 12
            x = quit_rect.right + gap
            y = quit_rect.centery - av_h // 2
            if x + av_w > self.width - 8: x = self.width - av_w - 8
            if y < 8: y = 8
            if y + av_h > self.height - 8: y = self.height - av_h - 8
            self.avatar_rect = pygame.Rect(x, y, av_w, av_h)

            lx = self.width - x - av_w
            ly = y - 30 
            self.left_avatar_rect = pygame.Rect(lx, ly, av_w, av_h)
            
            self.left_avatar = IsaiahNPCPixelArt(pos=(lx, ly), size=64, scale=2)

    def reset_idle(self):
        self.idle_timer = 0.0
        if self.show_idle_hint:
            self.show_idle_hint = False
            if hasattr(self, 'left_avatar') and self.left_avatar.state == 'wave':
                self.left_avatar.set_state('idle')

    def draw(self):
        self.screen.fill(self.felt_color)

        # Texture
        tex_color = (0, 0, 0, 18)
        tex_s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        step = 14
        for x in range(-self.height, self.width, step):
            pygame.draw.line(tex_s, tex_color, (x, 0), (x + self.height, self.height), 1)
        self.screen.blit(tex_s, (0, 0))

        if self.vignette_surf:
            self.screen.blit(self.vignette_surf, (0, 0))

        if self.chips_enabled:
            for p in self.particles: p.draw(self.screen)
        if self.dice_enabled:
            for d in self.dice_particles: d.draw(self.screen)

        # Cinematic Dimming
        is_ultimate = hasattr(self, 'left_avatar') and self.left_avatar.state == 'judgment_storm'
        ui_alpha = 0.3 if is_ultimate else 1.0

        # Title
        title_text = self.title_text
        title_col = (245, 245, 245) if not is_ultimate else (100, 100, 100)
        gold_col = (212, 175, 55) if not is_ultimate else (80, 70, 20)
        
        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_r = shadow.get_rect(center=(self.width // 2, 60))
        self.screen.blit(shadow, (shadow_r.x + 4, shadow_r.y + 4))

        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            t = self.title_font.render(title_text, True, gold_col)
            tr = t.get_rect(center=(self.width // 2 + ox, 60 + oy))
            self.screen.blit(t, tr)

        title = self.title_font.render(title_text, True, title_col)
        tr = title.get_rect(center=(self.width // 2, 60))
        self.screen.blit(title, tr)

        # Buttons
        for b in self.buttons:
            b.draw(self.screen, alpha_mult=ui_alpha)

        # Avatars
        if self.avatar_enabled:
            # --- LEFT AVATAR (ISAIAH) ---
            if hasattr(self, 'left_avatar'):
                self.left_avatar.update()
                self.left_avatar.draw(self.screen)
                
                lar = self.left_avatar_rect
                text_to_show = None
                
                if self.Isaiah_npc_hover:
                    text_to_show = self.Isaiah_npc_hints[self.Isaiah_npc_index]
                    glow = pygame.Surface((lar.width+6, lar.height+6), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (212,175,55,80), glow.get_rect(), border_radius=6)
                    self.screen.blit(glow, (lar.x-3, lar.y-3))
                elif self.show_idle_hint:
                    text_to_show = "Psst... Click me!"

                if text_to_show:
                    tip_font = pygame.font.SysFont('Arial', 18)
                    lines = []
                    max_line_length = 32
                    words = text_to_show.split()
                    line = ''
                    for word in words:
                        if len(line + ' ' + word) > max_line_length:
                            lines.append(line)
                            line = word
                        else:
                            line += ' ' + word if line else word
                    if line: lines.append(line)
                    
                    tip_surfs = [tip_font.render(l, True, (245,245,245)) for l in lines]
                    pad = 6
                    tip_w = max(s.get_width() for s in tip_surfs) + pad*2
                    tip_h = sum(s.get_height() for s in tip_surfs) + pad*2 + (len(tip_surfs)-1)*2
                    tip_x = max(lar.x - tip_w + lar.width//2, 8)
                    tip_y = max(lar.y - tip_h - 10, 8)
                    
                    box = pygame.Surface((tip_w, tip_h), pygame.SRCALPHA)
                    box.fill((0,0,0,170))
                    pygame.draw.rect(box, (212,175,55), box.get_rect(), 1, border_radius=6)
                    self.screen.blit(box, (tip_x, tip_y))
                    y_offset = pad
                    for s in tip_surfs:
                        self.screen.blit(s, (tip_x + pad, tip_y + y_offset))
                        y_offset += s.get_height() + 2

            # --- RIGHT AVATAR (FULL ORIGINAL CODE) ---
            if not is_ultimate:
                ar = self.avatar_rect
                panel = pygame.Surface(ar.size, pygame.SRCALPHA)
                panel.fill((0, 0, 0, 70))
                self.screen.blit(panel, ar.topleft)

                # Geometry & Calculations
                head_r = max(6, ar.width // 4)
                head_x = ar.x + ar.width // 2
                head_y = ar.y + head_r + 4
                body_w = int(ar.width * 0.8)
                body_h = int(ar.height * 0.30)
                body_x = head_x - body_w // 2
                body_y = head_y + head_r - 2
                
                # Legs
                leg_w = int(body_w * 0.42)
                leg_h = max(8, int(ar.height * 0.32))
                leg_gap = max(2, int(body_w * 0.08))
                leg1_x = head_x - leg_w - leg_gap//2
                leg2_x = head_x + leg_gap//2
                leg_y = body_y + body_h - 2
                
                # Arms
                arm_w = max(4, int(body_w * 0.18))
                arm_h = int(body_h * 0.9)
                arm1_x = body_x - arm_w + 2
                arm2_x = body_x + body_w - 2
                arm_y = body_y + 2

                # Colors
                skin, hoodie, hoodie_outline = (255, 230, 180), (90, 0, 30), (50, 0, 15)
                pants, outline = (30, 30, 40), (20, 20, 20)
                hair_color, beard_color = (245, 220, 100), (180, 140, 80)

                # Draw Head
                pygame.draw.circle(self.screen, skin, (head_x, head_y), head_r)
                pygame.draw.circle(self.screen, outline, (head_x, head_y), head_r, 1)
                
                # Hair
                top_h = head_r + 6
                top_rect = pygame.Rect(head_x - head_r - 2, head_y - head_r - 4, head_r * 2 + 4, top_h)
                pygame.draw.ellipse(self.screen, hair_color, top_rect)
                pygame.draw.ellipse(self.screen, (200,170,70), top_rect, 1)
                band_h = head_r // 2 + 2
                band_rect = pygame.Rect(head_x - head_r + 2, head_y - head_r//2, head_r * 2 - 4, band_h)
                pygame.draw.rect(self.screen, hair_color, band_rect, border_radius=band_h//2)
                pygame.draw.rect(self.screen, (200,170,70), band_rect, 1, border_radius=band_h//2)

                # Face
                eye_r = max(1, head_r // 5)
                eye_y = head_y - eye_r
                pygame.draw.circle(self.screen, (0,0,0), (head_x - eye_r*2, eye_y), eye_r)
                pygame.draw.circle(self.screen, (0,0,0), (head_x + eye_r*2, eye_y), eye_r)

                # Beard & Mouth
                beard_height = head_r // 2 + 2
                beard_rect = pygame.Rect(head_x - head_r + 3, head_y - 2, head_r*2 - 6, beard_height)
                pygame.draw.rect(self.screen, beard_color, beard_rect, border_radius=head_r//2)
                mouth_skin_r = max(3, head_r // 3)
                pygame.draw.circle(self.screen, skin, (head_x, head_y + head_r//4), mouth_skin_r)
                mouth_rect = pygame.Rect(head_x - mouth_skin_r, head_y + head_r//4 - mouth_skin_r//2, mouth_skin_r*2, mouth_skin_r)
                pygame.draw.arc(self.screen, (0,0,0), mouth_rect, math.pi*0.15, math.pi - math.pi*0.15, 1)

                # Hoodie Body
                pygame.draw.rect(self.screen, hoodie, (body_x, body_y, body_w, body_h), border_radius=4)
                pygame.draw.rect(self.screen, hoodie_outline, (body_x, body_y, body_w, body_h), 1, border_radius=4)
                
                # Pocket & Logo
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
                
                if self.avatar_hover:
                    glow = pygame.Surface((ar.width+6, ar.height+6), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (212,175,55,80), glow.get_rect(), border_radius=6)
                    self.screen.blit(glow, (ar.x-3, ar.y-3))
                    snippet = self.rule_snippets[self.current_rule_index]
                    tip_surf = self.font.render(snippet, True, (245,245,245))
                    tip_x = ar.right + 10 if ar.right + 10 + tip_surf.get_width() < self.width else ar.x
                    tip_y = ar.y if ar.right + 10 + tip_surf.get_width() < self.width else ar.y - 40
                    self.screen.blit(tip_surf, (tip_x, tip_y))

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.result = 'quit'
            
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self.reset_idle()

            for b in self.buttons:
                b.handle_event(event)

            if event.type == pygame.KEYDOWN:
                self.input_buffer.append(event.key)
                if len(self.input_buffer) > len(self.konami_code):
                    self.input_buffer.pop(0)
                
                if self.input_buffer == self.konami_code:
                    if hasattr(self, 'left_avatar'):
                        self.left_avatar.set_state('judgment_storm')
                        self.input_buffer = []

                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.buttons)
                    for i, b in enumerate(self.buttons): b.hovered = (i == self.selected)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.buttons)
                    for i, b in enumerate(self.buttons): b.hovered = (i == self.selected)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.buttons[self.selected].callback()
            
            if self.avatar_enabled:
                if event.type == pygame.MOUSEMOTION:
                    self.avatar_hover = self.avatar_rect.collidepoint(event.pos)
                    self.Isaiah_npc_hover = self.left_avatar_rect.collidepoint(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.avatar_rect.collidepoint(event.pos):
                        self.current_rule_index = (self.current_rule_index + 1) % len(self.rule_snippets)
                    if self.left_avatar_rect.collidepoint(event.pos):
                        self.hint_cycle_pos += 1
                        if self.hint_cycle_pos >= len(self.hint_indices):
                            random.shuffle(self.hint_indices)
                            self.hint_cycle_pos = 0
                        self.Isaiah_npc_index = self.hint_indices[self.hint_cycle_pos]
                        
                        if hasattr(self, 'left_avatar'):
                            anim = self.hint_animation_map.get(self.Isaiah_npc_index)
                            if anim is None:
                                anim = random.choice(['idle', 'blink'])
                            self.left_avatar.set_state(anim)

    def run(self) -> str:
        self.result = None
        while self.result is None:
            ms = self.clock.tick(60)
            dt = ms / 1000.0
            
            self.idle_timer += dt
            if self.idle_timer > 5.0 and not self.show_idle_hint and not self.idle_hint_shown_once:
                self.show_idle_hint = True
                self.idle_hint_shown_once = True 
                if hasattr(self, 'left_avatar'):
                    self.left_avatar.set_state('wave')

            self.handle_events()
            
            if self.chips_enabled: self.update_particles(dt)
            if self.dice_enabled: self.update_dice(dt)
            if self.avatar_enabled and self.avatar_hover:
                self.rule_cycle_timer += dt
                if self.rule_cycle_timer >= self.rule_cycle_interval:
                    self.rule_cycle_timer = 0.0
                    self.current_rule_index = (self.current_rule_index + 1) % len(self.rule_snippets)
            self.draw()
        return self.result

    def update_particles(self, dt: float) -> None:
        self.spawn_timer -= dt
        if self.spawn_timer <= 0.0:
            self.spawn_timer += self.spawn_interval
            for _ in range(random.randint(1, 2)):
                if len(self.particles) >= self.max_particles: break
                x = random.uniform(self.width * 0.32, self.width * 0.68)
                y = -20.0
                vx, vy = random.uniform(-40.0, 40.0), random.uniform(80.0, 140.0)
                r, color = random.uniform(10.0, 18.0), random.choice(self.chip_colors)
                self.particles.append(ChipParticle(x, y, vx, vy, r, color))
        alive = []
        for p in self.particles:
            p.update(dt, self.gravity)
            if not p.is_offscreen(self.height + 60): alive.append(p)
        self.particles = alive

    def update_dice(self, dt: float) -> None:
        self.dice_spawn_timer -= dt
        if self.dice_spawn_timer <= 0.0:
            self.dice_spawn_timer += self.dice_spawn_interval
            if len(self.dice_particles) < self.max_dice and random.random() < 0.7:
                x = random.uniform(self.width * 0.3, self.width * 0.7)
                y = -30.0
                vx, vy = random.uniform(-20, 20), random.uniform(150, 250)
                size = random.uniform(24, 36)
                val = random.randint(1, 6)
                self.dice_particles.append(DiceParticle(x, y, vx, vy, size, val))
        alive = []
        for d in self.dice_particles:
            d.update(dt, self.gravity)
            if not d.is_offscreen(self.height + 60): alive.append(d)
        self.dice_particles = alive