import pygame
import random
import math

# --- Configuration & Palette ---
PALETTE = {
    'skin': (235, 210, 190),
    'skin_shadow': (200, 170, 150),
    'hair_main': (40, 40, 45),
    'coat_main': (50, 60, 80),
    'coat_trim': (180, 180, 190),
    'shirt': (220, 220, 225),
    'pants': (35, 40, 50),
    'shoes': (20, 20, 20),
    'mask': (60, 65, 75), 
    'katana_sheath': (30, 30, 30),
    'katana_wrap': (160, 50, 50),
    'gold': (210, 180, 50),
    'outline': (15, 15, 20),
    'shadow': (0, 0, 0, 80),
    'fruit_red': (220, 60, 60),
    'fruit_green': (100, 200, 60),
    'fruit_yellow': (240, 220, 50),
    'fruit_inside': (255, 250, 220),
    'slash_fx': (255, 255, 255),
    'teleport_fx': (100, 255, 255), 
    'lightning': (150, 220, 255)    
}

class IsaiahNPCPixelArt:
    def __init__(self, pos=(100, 40), size=64, scale=3):
        self.pos = pos
        self.size = size
        self.scale = scale 
        self.animations = self._create_animations()
        self.state = 'idle'
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        
        self.state_durations = {
            'fruit_ninja': 40, 
            'fruit_combo': 35, 
            'judgment_storm': 45, 
            'default': 180
        }

    def _create_animations(self):
        ninja_len = 90
        combo_len = 135 
        storm_len = 110 
        
        return {
            'idle':   [self._draw_idle, self._draw_idle, self._draw_idle_breath],
            'blink':  [self._draw_blink, self._draw_blink],
            'wave':   [self._draw_wave1, self._draw_wave2, self._draw_wave1, self._draw_idle],
            'walk':   [self._draw_walk1, self._draw_walk2, self._draw_walk3, self._draw_walk4],
            'bounce': [self._draw_bounce1, self._draw_bounce2, self._draw_bounce1, self._draw_idle],
            'fruit_ninja': [self._draw_fruit_ninja] * ninja_len,
            'fruit_combo': [self._draw_fruit_combo] * combo_len,
            'judgment_storm': [self._draw_judgment_storm] * storm_len
        }

    def set_state(self, state):
        if state in self.animations:
            self.state = state
            self.frame = 0
            self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        duration = self.state_durations.get(self.state, self.state_durations['default'])
        
        if now - self.last_update > duration:
            self.frame = (self.frame + 1) % len(self.animations[self.state])
            self.last_update = now
            
            if self.state == 'idle' and random.random() < 0.02:
                self.set_state(random.choice(['blink', 'bounce']))
            
            if self.frame == 0 and self.state != 'idle':
                self.set_state('idle')

    def draw(self, surface):
        canvas_w = self.size * 4
        canvas_h = self.size * 5 
        
        temp_surface = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
        
        offset_x = int(self.size * 3.0) 
        offset_y = int(self.size * 3.5) 

        original_pos = self.pos
        self.pos = (offset_x, offset_y) 
        
        frame_func = self.animations[self.state][self.frame]
        frame_func(temp_surface)
        
        self.pos = original_pos 
        
        final_w = int(canvas_w * self.scale)
        final_h = int(canvas_h * self.scale)
        scaled_surface = pygame.transform.scale(temp_surface, (final_w, final_h))
        
        draw_x = self.pos[0] - (offset_x * self.scale)
        draw_y = self.pos[1] - (offset_y * self.scale)
        
        surface.blit(scaled_surface, (draw_x, draw_y))

    # --- Standard Animations ---
    def _draw_idle(self, surface): self._draw_base(surface, anim_y=0)
    def _draw_idle_breath(self, surface): self._draw_base(surface, anim_y=1)
    def _draw_blink(self, surface): self._draw_base(surface, eyes_open=False, anim_y=0)
    def _draw_wave1(self, surface): self._draw_base(surface, arm_wave=True, wave_angle=-20)
    def _draw_wave2(self, surface): self._draw_base(surface, arm_wave=True, wave_angle=10)
    # Improved Walk Cycle
    def _draw_walk1(self, surface): self._draw_base(surface, anim_y=1, leg_offset=4, arm_swing=4)
    def _draw_walk2(self, surface): self._draw_base(surface, anim_y=0, leg_offset=0, arm_swing=0)
    def _draw_walk3(self, surface): self._draw_base(surface, anim_y=1, leg_offset=-4, arm_swing=-4)
    def _draw_walk4(self, surface): self._draw_base(surface, anim_y=0, leg_offset=0, arm_swing=0)

    def _draw_bounce1(self, surface): self._draw_base(surface, anim_y=4)
    def _draw_bounce2(self, surface): self._draw_base(surface, anim_y=-2)

    # --- ANIMATION 1: SINGLE BIG THROW ---
    def _draw_fruit_ninja(self, surface):
        f = self.frame
        t_throw, t_slice = 6, 60
        
        fruits = []
        if f >= t_throw and f < 90:
            t = f - t_throw
            g = 0.5
            v0 = 14.5 
            x_offsets = [-8, 0, 8] 
            colors = [PALETTE['fruit_red'], PALETTE['fruit_green'], PALETTE['fruit_yellow']]
            for i in range(3):
                fx = x_offsets[i] * (1 + t/50)
                fy = -(v0 * t - 0.5 * g * (t*t))
                start_y = -35
                is_sliced = f >= t_slice
                fruits.append({'x': fx, 'y': start_y + fy, 'color': colors[i], 'sliced': is_sliced, 'slice_t': f-t_slice})

        if f < t_throw: self._draw_base(surface, anim_y=4, override_l_arm=True, l_arm_pos=(4, 10))
        elif f < t_throw + 5: self._draw_base(surface, anim_y=-2, override_l_arm=True, l_arm_pos=(-6, -15)) 
        elif f < t_slice: self._draw_base(surface, anim_y=1 if (f//8)%2==0 else 0, eyes_open=False, override_l_arm=True, l_arm_pos=(-8, 6))
        elif f == t_slice:
            self._draw_base(surface, anim_y=2, eyes_open=True, override_l_arm=True, l_arm_pos=(-25, -5), unsheathed=True)
            cx, cy = self.pos[0] + self.size // 2, self.pos[1] + self.size - 10
            slash_y = cy - 80 
            pygame.draw.line(surface, PALETTE['slash_fx'], (cx - 50, slash_y + 10), (cx + 50, slash_y - 10), 4)
        elif f < t_slice + 25: self._draw_base(surface, anim_y=2, override_l_arm=True, l_arm_pos=(-22, -2), unsheathed=True)
        elif f < t_slice + 40:
            progress = (f - (t_slice + 25)) / 15.0
            lx, ly = -22 + (14 * progress), -2 + (8 * progress)
            self._draw_base(surface, anim_y=0, override_l_arm=True, l_arm_pos=(lx, ly), unsheathed=True)
        else: self._draw_base(surface, anim_y=0)
        self._render_fruits(surface, fruits)

    # --- ANIMATION 2: FRUIT COMBO ---
    def _draw_fruit_combo(self, surface):
        f = self.frame
        t_throw_1, t_throw_2, t_throw_3 = 5, 12, 19
        t_slash_1, t_slash_2, t_slash_3 = 55, 65, 75
        t_vanish, t_reappear = 115, 120
        
        g, v0, start_y = 0.4, 11.5, -35
        fruits = []
        def calc_fruit_pos(throw_time, current_time, x_vel):
            t = current_time - throw_time
            if t < 0: return None
            fx = (x_vel * t)
            fy = start_y - (v0 * t - 0.5 * g * (t*t))
            return fx, fy

        pos1 = calc_fruit_pos(t_throw_1, f, -0.6) 
        if pos1 and f < t_vanish:
            fruits.append({'x': pos1[0], 'y': pos1[1], 'color': PALETTE['fruit_red'], 'sliced': f>=t_slash_1, 'slice_t': f-t_slash_1})
        pos2 = calc_fruit_pos(t_throw_2, f, -1.2)
        if pos2 and f < t_vanish:
            fruits.append({'x': pos2[0], 'y': pos2[1], 'color': PALETTE['fruit_green'], 'sliced': f>=t_slash_2, 'slice_t': f-t_slash_2})
        pos3 = calc_fruit_pos(t_throw_3, f, -1.8)
        if pos3 and f < t_vanish:
            fruits.append({'x': pos3[0], 'y': pos3[1], 'color': PALETTE['fruit_yellow'], 'sliced': f>=t_slash_3, 'slice_t': f-t_slash_3})

        if f < 45:
            if (f >= t_throw_1 and f < t_throw_1+5) or (f >= t_throw_2 and f < t_throw_2+5) or (f >= t_throw_3 and f < t_throw_3+5):
                arm_pos = (-6, -15) 
            else:
                arm_pos = (-8, 6)
            self._draw_base(surface, body_x_offset=0, override_l_arm=True, l_arm_pos=arm_pos, unsheathed=False)
        elif f < t_vanish:
            unsheathed = True
            if f < t_slash_1:
                progress = (f - 45) / (t_slash_1 - 45)
                body_x = -25 * progress
            elif f < t_slash_2:
                progress = (f - t_slash_1) / (t_slash_2 - t_slash_1)
                body_x = -25 + (-25 * progress)
            elif f < t_slash_3:
                progress = (f - t_slash_2) / (t_slash_3 - t_slash_2)
                body_x = -50 + (-25 * progress)
            else:
                body_x = -75
                
            if (f < t_slash_1) or (f > t_slash_1 and f < t_slash_2) or (f > t_slash_2 and f < t_slash_3):
                arm_pos = (12, 4); pose_y = 2 if (f % 4 < 2) else 0
            elif f == t_slash_1 or f == t_slash_2 or f == t_slash_3:
                arm_pos = (-30, -5); pose_y = 2
                self._draw_slash_fx(surface, body_x, -70)
            elif f > t_slash_3:
                 arm_pos = (12, 6); unsheathed = True; pose_y = 0

            self._draw_base(surface, anim_y=pose_y if 'pose_y' in locals() else 0, 
                            body_x_offset=body_x, override_l_arm=True, l_arm_pos=arm_pos, unsheathed=unsheathed)
        
        else:
            cx_vanish = self.pos[0] + self.size // 2 - 75
            cy = self.pos[1] + self.size - 20 
            
            if f >= t_vanish and f < t_reappear:
                if f < t_vanish + 3:
                    rect = pygame.Rect(cx_vanish - 10, cy - 100, 20, 110)
                    pygame.draw.rect(surface, PALETTE['teleport_fx'], rect)
                    pygame.draw.rect(surface, (255, 255, 255), rect.inflate(-8, 0))
            elif f >= t_reappear:
                cx_origin = self.pos[0] + self.size // 2
                if f < t_reappear + 4:
                    rect = pygame.Rect(cx_origin - 10, cy - 100, 20, 110)
                    pygame.draw.rect(surface, PALETTE['teleport_fx'], rect)
                    pygame.draw.rect(surface, (255, 255, 255), rect.inflate(-8, 0))
                if f >= t_reappear + 2:
                    self._draw_base(surface, body_x_offset=0)

        self._render_fruits(surface, fruits)

    # --- ANIMATION 3: JUDGMENT STORM ---
    def _draw_judgment_storm(self, surface):
        f = self.frame
        t_vanish, t_slashes, t_reappear, t_impact = 25, 30, 60, 90

        cx, cy = self.pos[0] + self.size // 2, self.pos[1] + self.size - 10

        if f < t_vanish:
            shake_x = random.choice([-1, 1]) if f % 2 == 0 else 0
            self._draw_base(surface, body_x_offset=shake_x, anim_y=4, eyes_open=False, override_l_arm=True, l_arm_pos=(-8, 6))
            if f > 10 and random.random() < 0.3:
                lx = cx + random.randint(-30, 30)
                ly = cy + random.randint(-40, 0)
                pygame.draw.line(surface, PALETTE['lightning'], (lx, ly), (lx+5, ly+5), 2)
        elif f < t_slashes: pass 
        elif f < t_reappear:
            if random.random() < 0.5:
                sx1, sy1 = random.randint(0, self.size*4), random.randint(0, self.size*3)
                sx2, sy2 = sx1 + random.randint(-40, 40), sy1 + random.randint(-40, 40)
                pygame.draw.line(surface, PALETTE['slash_fx'], (sx1, sy1), (sx2, sy2), 2)
                overlay = pygame.Surface((self.size*4, self.size*5), pygame.SRCALPHA)
                overlay.fill((150, 220, 255, 20))
                surface.blit(overlay, (0,0))
        elif f < t_impact:
            unsheathed = True
            arm_pos = (-25, 5) 
            if f >= 70:
                progress = (f - 70) / (t_impact - 70)
                lx, ly = -25 + (17 * progress), 5 + (1 * progress)
                arm_pos = (lx, ly)
            self._draw_base(surface, anim_y=0, override_l_arm=True, l_arm_pos=arm_pos, unsheathed=unsheathed)
        elif f == t_impact:
             self._draw_base(surface, anim_y=0, unsheathed=False)
             flash = pygame.Surface((self.size*4, self.size*5))
             flash.fill((255, 255, 255))
             surface.blit(flash, (0,0))
        else: self._draw_base(surface, anim_y=0)

    def _render_fruits(self, surface, fruits):
        cx, cy = self.pos[0] + self.size // 2, self.pos[1] + self.size - 10
        for fruit in fruits:
            screen_x = cx + fruit['x']
            screen_y = cy + fruit['y']
            
            if not fruit['sliced']:
                pygame.draw.circle(surface, fruit['color'], (int(screen_x), int(screen_y)), 4)
                pygame.draw.circle(surface, (255,255,255), (int(screen_x)-1, int(screen_y)-1), 1)
            else:
                dt = fruit['slice_t']
                split_dist = dt * 1.5
                gravity = dt * 2.0
                pygame.draw.arc(surface, fruit['color'], (screen_x - 4 - split_dist, screen_y - 4 + gravity, 8, 8), 0, 3.14, 4)
                pygame.draw.line(surface, PALETTE['fruit_inside'], (screen_x - 4 - split_dist, screen_y + gravity), (screen_x + 4 - split_dist, screen_y + gravity), 2)
                pygame.draw.arc(surface, fruit['color'], (screen_x - 4 + split_dist, screen_y - 4 + gravity, 8, 8), 3.14, 6.28, 4)
                pygame.draw.line(surface, PALETTE['fruit_inside'], (screen_x - 4 + split_dist, screen_y + gravity), (screen_x + 4 + split_dist, screen_y + gravity), 2)

    def _draw_slash_fx(self, surface, body_offset_x, height_offset):
        cx, cy = self.pos[0] + self.size // 2 + body_offset_x, self.pos[1] + self.size - 10 + height_offset
        offset = random.choice([-10, 10])
        pygame.draw.line(surface, PALETTE['slash_fx'], (cx - 40, cy + 20 + offset), (cx + 40, cy - 20 + offset), 3)

    # --- Core Visuals ---
    def _draw_base(self, surface, eyes_open=True, arm_wave=False, wave_angle=0, 
                   anim_y=0, leg_offset=0, body_x_offset=0, arm_swing=0,
                   override_l_arm=False, l_arm_pos=(0,0), unsheathed=False):
        
        x, y = self.pos 
        s = self.size
        cx = x + s // 2 + int(body_x_offset)
        cy = y + s - 10 

        # Shadow moved down (Keep new position)
        shadow_rect = pygame.Rect(cx - 12, cy - 1, 24, 6)
        pygame.draw.ellipse(surface, PALETTE['shadow'], shadow_rect)

        body_w, body_h = 20, 24
        body_y = cy - 32 + anim_y
        
        leg_w, leg_h = 6, 14
        l_leg_x = cx - body_w//2 + 3
        pygame.draw.rect(surface, PALETTE['pants'], (l_leg_x + leg_offset, body_y + body_h - 4, leg_w, leg_h))
        pygame.draw.rect(surface, PALETTE['shoes'], (l_leg_x + leg_offset - 1, body_y + body_h + leg_h - 4, leg_w + 2, 3))
        r_leg_x = cx + body_w//2 - leg_w - 3
        pygame.draw.rect(surface, PALETTE['pants'], (r_leg_x - leg_offset, body_y + body_h - 4, leg_w, leg_h))
        pygame.draw.rect(surface, PALETTE['shoes'], (r_leg_x - leg_offset - 1, body_y + body_h + leg_h - 4, leg_w + 2, 3))

        pygame.draw.rect(surface, PALETTE['shirt'], (cx - body_w//2 + 4, body_y, body_w - 8, body_h))
        coat_rect = pygame.Rect(cx - body_w//2, body_y, body_w, body_h)
        pygame.draw.rect(surface, PALETTE['coat_main'], coat_rect, border_radius=2)
        pygame.draw.rect(surface, PALETTE['shirt'], (cx - 3, body_y + 2, 6, body_h - 4))
        pygame.draw.line(surface, PALETTE['coat_trim'], (cx - body_w//2, body_y), (cx - body_w//2, body_y + body_h), 1)
        pygame.draw.line(surface, PALETTE['coat_trim'], (cx + body_w//2 - 1, body_y), (cx + body_w//2 - 1, body_y + body_h), 1)

        katana_x, katana_y = cx - body_w//2 - 2, body_y + 10
        end_x, end_y = katana_x - 10, katana_y + 12
        pygame.draw.line(surface, PALETTE['katana_sheath'], (katana_x, katana_y), (end_x, end_y), 4)
        pygame.draw.line(surface, PALETTE['gold'], (katana_x - 6, katana_y + 8), (katana_x - 5, katana_y + 9), 4) 

        if not unsheathed:
            pygame.draw.rect(surface, PALETTE['gold'], (katana_x - 2, katana_y - 2, 6, 3)) 
            handle_end_x, handle_end_y = katana_x + 6, katana_y - 6
            pygame.draw.line(surface, PALETTE['skin'], (katana_x, katana_y), (handle_end_x, handle_end_y), 3)
            pygame.draw.line(surface, PALETTE['katana_wrap'], (katana_x, katana_y), (handle_end_x, handle_end_y), 3)

        head_r = 10
        head_x, head_y = cx, body_y - head_r + 3
        pygame.draw.rect(surface, PALETTE['skin_shadow'], (head_x - 3, head_y + 6, 6, 4))
        pygame.draw.circle(surface, PALETTE['skin'], (head_x, head_y), head_r)
        
        # --- REVERTED HEAD ART ---
        # Mask (High position)
        mask_color = PALETTE['mask']
        pygame.draw.rect(surface, mask_color, (head_x - 9, head_y + 2, 18, 7))
        pygame.draw.rect(surface, mask_color, (head_x - 6, head_y + 9, 12, 2))

        eye_y = head_y - 1
        if eyes_open:
            pygame.draw.rect(surface, (255, 255, 255), (head_x - 5, eye_y - 1, 3, 3))
            pygame.draw.rect(surface, (255, 255, 255), (head_x + 2, eye_y - 1, 3, 3))
            pygame.draw.rect(surface, (20, 20, 30), (head_x - 4, eye_y, 1, 1))
            pygame.draw.rect(surface, (20, 20, 30), (head_x + 3, eye_y, 1, 1))
        else:
            pygame.draw.line(surface, (60, 50, 40), (head_x - 5, eye_y), (head_x - 2, eye_y), 1)
            pygame.draw.line(surface, (60, 50, 40), (head_x + 2, eye_y), (head_x + 5, eye_y), 1)

        pygame.draw.circle(surface, PALETTE['hair_main'], (head_x, head_y - 2), head_r + 1)
        # Bangs (Reverted to full coverage)
        pygame.draw.polygon(surface, PALETTE['hair_main'], [
            (head_x - head_r, head_y - 3), (head_x - 3, head_y + 2), (head_x, head_y - 3),
            (head_x + 4, head_y + 2), (head_x + head_r, head_y - 5), (head_x, head_y - head_r - 1)
        ])

        arm_w, arm_l = 5, 16
        r_arm_x, r_arm_y = cx + body_w//2, body_y + 2
        # Right arm (swings opposite to left arm/leg)
        r_arm_swing = -arm_swing if arm_swing != 0 else 0
        pygame.draw.rect(surface, PALETTE['coat_main'], (r_arm_x - 1 + r_arm_swing, r_arm_y, arm_w, arm_l), border_radius=2)
        pygame.draw.circle(surface, PALETTE['skin'], (r_arm_x + 1 + r_arm_swing, r_arm_y + arm_l), 3)

        l_arm_x, l_arm_y = cx - body_w//2 - arm_w + 1, body_y + 2
        if override_l_arm:
            dx, dy = l_arm_pos
            hand_x, hand_y = l_arm_x + dx, l_arm_y + dy + arm_l
            pygame.draw.line(surface, PALETTE['coat_main'], (l_arm_x+2, l_arm_y+2), (hand_x, hand_y-2), 5)
            pygame.draw.circle(surface, PALETTE['skin'], (hand_x, hand_y), 3)
            if unsheathed:
                sword_len = 24
                if dx > 0: tip_x, tip_y = hand_x + 20, hand_y - 10 
                else: tip_x, tip_y = hand_x - 20, hand_y - 5
                pygame.draw.line(surface, PALETTE['katana_wrap'], (hand_x, hand_y), (hand_x - (tip_x-hand_x)*0.25, hand_y - (tip_y-hand_y)*0.25), 3)
                pygame.draw.line(surface, (220, 220, 220), (hand_x, hand_y), (tip_x, tip_y), 2)
                pygame.draw.rect(surface, PALETTE['gold'], (hand_x - 2, hand_y - 2, 4, 4))
        elif arm_wave:
            wave_rad = math.radians(wave_angle)
            wx, wy = l_arm_x - 8 + (wave_angle * 0.2), l_arm_y - 12
            pygame.draw.rect(surface, PALETTE['coat_main'], (wx, wy, arm_w, arm_l), border_radius=2)
            pygame.draw.circle(surface, PALETTE['skin'], (wx + 2, wy - 2), 4)
        else:
            l_arm_swing = arm_swing
            pygame.draw.rect(surface, PALETTE['coat_main'], (l_arm_x + l_arm_swing, l_arm_y, arm_w, arm_l), border_radius=2)
            pygame.draw.circle(surface, PALETTE['skin'], (l_arm_x + 2 + l_arm_swing, l_arm_y + arm_l), 3)

class IsaiahAvatar:
    def __init__(self, rect): self.rect = rect
    def draw(self, surface):
        ar = self.rect
        panel = pygame.Surface(ar.size, pygame.SRCALPHA)
        panel.fill((0, 0, 0, 90))
        surface.blit(panel, ar.topleft)
        head_r = max(6, ar.width // 4)
        head_x, head_y = ar.x + ar.width // 2, ar.y + head_r + 4
        pygame.draw.circle(surface, PALETTE['coat_main'], (head_x, head_y + 15), head_r + 4)
        pygame.draw.circle(surface, PALETTE['hair_main'], (head_x, head_y), head_r)
        pygame.draw.circle(surface, PALETTE['skin'], (head_x, head_y + 2), head_r - 2)
        
        # Reverted Avatar Hair/Mask
        pygame.draw.polygon(surface, PALETTE['hair_main'], [
            (head_x - head_r, head_y - 3), (head_x - 3, head_y + 2), (head_x, head_y - 3),
            (head_x + 4, head_y + 2), (head_x + head_r, head_y - 5), (head_x, head_y - head_r - 1)
        ])
        pygame.draw.rect(surface, PALETTE['mask'], (head_x - 9, head_y + 4, 18, 10))

class IsaiahNPC:
    def __init__(self, screen, font=None, image_path=None):
        self.screen = screen
        self.font = font or pygame.font.SysFont('Arial', 22)
        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.smoothscale(self.image, (80, 80))
            except Exception: self.image = None
        self.text = "Hi, I'm Isaiah the NPC!"
        self.visible = True
    def draw(self):
        if not self.visible: return
        box_w, box_h = 420, 180
        x, y = 20, 40
        s = pygame.Surface((box_w, box_h))
        s.set_alpha(230)
        s.fill((40, 35, 45))
        self.screen.blit(s, (x, y))
        pygame.draw.rect(self.screen, (100, 100, 120), (x, y, box_w, box_h), 2)
        if self.image:
            self.screen.blit(self.image, (x + 16, y + 16))
            pygame.draw.rect(self.screen, (200, 200, 200), (x + 16, y + 16, 80, 80), 1)
        lines = self.text.split('\n')
        text_x = x + 110 if self.image else x + 16
        text_y = y + 16
        for i, line in enumerate(lines):
            color = (255, 200, 100) if i == 0 else (220, 220, 230)
            txt = self.font.render(line, True, color)
            self.screen.blit(txt, (text_x, text_y))
            text_y += self.font.get_height() + 4