import pygame


class RedHoodiePixelAvatar:
    """A small procedural pixel-art avatar for the red-hoodie character.

    Draws into a tiny pixel canvas (width x height) and provides a few
    animation frames (idle breathe + blink). The result is scaled with
    nearest-neighbor when drawn to preserve chunky pixels.
    """

    def __init__(self, pixel_size=(16, 24), palette=None, anim_rate=220):
        # pixel canvas size (w, h)
        self.pw, self.ph = pixel_size
        self.anim_rate = anim_rate  # ms per frame
        self.frames = []
        self.animations = {}
        self.state = 'idle'
        self.frame_index = 0
        self.last = pygame.time.get_ticks()
        self.state_end_time = None

        # default palette
        self.palette = palette or {
            'skin': (235, 200, 170),
            'skin_shadow': (200, 160, 120),
            # hoodie colors
            'hood': (160, 24, 24),
            'hood_dark': (110, 10, 10),
            'trim': (220, 180, 80),
            # default hair is now blonde for this avatar
            'hair': (245, 220, 100),
            'beard': (180, 140, 80),
            'outline': (12, 12, 14),
            'eye': (18, 18, 20),
            'accent': (255, 255, 255),
        }

        self._build_frames()
        # animations dict: name -> list of frames
        self.animations['idle'] = self.frames
        self.animations['coding'] = self._build_coding_frames()
        self.animations['setup'] = self._build_setup_frames()
        self.animations['transition'] = self._build_transition_frames()

    def _make_canvas(self):
        return pygame.Surface((self.pw, self.ph), pygame.SRCALPHA)

    def _set_px(self, surf, x, y, col):
        # draw a single "pixel" as a 1x1 rect on the tiny canvas
        if 0 <= x < self.pw and 0 <= y < self.ph:
            surf.fill(col, (x, y, 1, 1))

    def _build_frames(self):
        # frame 0: idle
        f0 = self._make_canvas()
        self._draw_base(f0, breathe_offset=0, eyes_open=True)

        # frame 1: breathe (slight body/head offset)
        f1 = self._make_canvas()
        self._draw_base(f1, breathe_offset=1, eyes_open=True)

        # frame 2: blink
        f2 = self._make_canvas()
        self._draw_base(f2, breathe_offset=0, eyes_open=False)

        self.frames = [f0, f1, f0, f2]  # simple idle cycle

    def _build_coding_frames(self):
        # build a more detailed coding animation with head/torso bob and typing hands
        coding = []
        base = self.frames[0]
        n_frames = 12

        # Predefined simple code-line patterns to draw on the screen
        code_patterns = [
            ["def ", "foo()"],
            ["for i in range:", "  print(i)"],
            ["if x > 0:", "  x -= 1"],
            ["class A:", "  def __init__"],
        ]

        for i in range(n_frames):
            c = base.copy()

            # animate head bob / tilt by shifting head drawing area via applying a small offset
            head_shift = -1 if (i % 4 == 0) else (1 if (i % 4 == 2) else 0)

            # laptop placement relative to canvas
            lw = max(8, self.pw * 2 // 3)
            lh = max(4, self.ph // 7)
            lx = max(0, (self.pw - lw)//2)
            # put laptop slightly in front of body
            ly = int(self.ph * 0.55)

            # draw screen (with border)
            screen_col = (30, 34, 44)
            border_col = (10, 10, 12)
            for yy in range(lh):
                for xx in range(lw):
                    px = lx + xx
                    py = ly + yy
                    if 0 <= px < self.pw and 0 <= py < self.ph:
                        # border on top row/left/right
                        if yy == 0 or xx == 0 or xx == lw-1:
                            c.fill(border_col, (px, py, 1, 1))
                        else:
                            c.fill(screen_col, (px, py, 1, 1))

            # keyboard darker row below screen
            kb_y = ly + lh
            kb_w = lw
            for xx in range(kb_w):
                px = lx + xx
                if 0 <= px < self.pw and 0 <= kb_y < self.ph:
                    c.fill((18, 18, 24), (px, kb_y, 1, 1))

            # draw simple code lines on the screen using patterns, shifted per frame
            pattern = code_patterns[i % len(code_patterns)]
            # starting draw position inside screen
            text_x = lx + 2
            text_y = ly + 1
            # map characters to pixels (coarse)
            for row_idx, line in enumerate(pattern):
                for j, ch in enumerate(line):
                    if (i + j + row_idx) % 5 == 0:
                        # bright pixel (simulating text)
                        px = text_x + j
                        py = text_y + row_idx * 1
                        if 0 <= px < self.pw and 0 <= py < self.ph:
                            c.fill((160, 220, 140), (px, py, 1, 1))

            # subtle screen glow: paint adjacent pixels with low alpha-like color (approx)
            glow_col = (80, 120, 80)
            for gx in range(lx+1, lx+lw-1):
                gy = ly - 1
                if 0 <= gx < self.pw and 0 <= gy < self.ph:
                    # sprinkle a few glow pixels
                    if (gx + i) % 7 == 0:
                        c.fill(glow_col, (gx, gy, 1, 1))

            # typing hands: animate across kb_w
            hand_col = (235, 200, 170)
            # alternate left/right hand positions for more motion
            left_hand_x = lx + max(1, kb_w // 6) + (1 if i % 3 == 0 else 0)
            right_hand_x = lx + kb_w - max(2, kb_w // 6) - (1 if i % 3 == 1 else 0)
            hand_y = kb_y
            self._safe_set_px(c, left_hand_x, hand_y, hand_col)
            self._safe_set_px(c, right_hand_x, hand_y, hand_col)

            # small head tilt visual: shift a column of hair/skin
            # we'll nudge the top row of pixels by head_shift
            # find head area approximated as rows near top; apply a simple pixel move
            if head_shift != 0:
                for xx in range(self.pw):
                    for yy in range(1, 3):
                        src_x = xx
                        src_y = yy
                        dst_x = xx + head_shift
                        dst_y = yy
                        if 0 <= src_x < self.pw and 0 <= src_y < self.ph and 0 <= dst_x < self.pw:
                            # copy pixel color
                            col = c.get_at((src_x, src_y))
                            c.fill(col, (dst_x, dst_y, 1, 1))

            # blinking cursor: toggle every other frame
            if i % 2 == 0:
                cursor_x = lx + 2 + (i % max(1, lw-4))
                cursor_y = ly + 1
                if 0 <= cursor_x < self.pw and 0 <= cursor_y < self.ph:
                    c.fill((200, 250, 200), (cursor_x, cursor_y, 1, 1))

            coding.append(c)
        return coding

    def _build_setup_frames(self):
        # build frames where the avatar is at a desk / gaming setup coding
        setup = []
        n = 16
        for i in range(n):
            s = self._make_canvas()
            # draw avatar slightly shifted down to sit
            breathe = 0 if (i % 4 < 2) else 1
            self._draw_base(s, breathe_offset=breathe, eyes_open=True)

            w, h = self.pw, self.ph
            # desk: a wide rectangle near bottom
            desk_h = max(3, h // 6)
            desk_y = h - desk_h - 1
            for yy in range(desk_h):
                for xx in range(w - 2):
                    px = 1 + xx
                    py = desk_y + yy
                    s.fill((40, 20, 10), (px, py, 1, 1))

            # monitor on desk: centered rectangle
            mon_w = max(8, w - 8)
            mon_h = max(5, h // 4)
            mon_x = (w - mon_w) // 2
            mon_y = desk_y - mon_h - 1
            for yy in range(mon_h):
                for xx in range(mon_w):
                    px = mon_x + xx
                    py = mon_y + yy
                    if yy in (0, mon_h-1) or xx in (0, mon_w-1):
                        s.fill((10, 10, 12), (px, py, 1, 1))
                    else:
                        # fill screen with shifting code-like pixels
                        if (xx + yy + i) % 6 == 0:
                            s.fill((180, 240, 160), (px, py, 1, 1))
                        else:
                            s.fill((30, 36, 46), (px, py, 1, 1))

            # keyboard area: row on desk just below monitor
            kb_y = desk_y
            kb_x0 = mon_x + 1
            kb_w = mon_w - 2
            for kx in range(kb_w):
                if (kx + i) % 3 == 0:
                    s.fill((20, 20, 28), (kb_x0 + kx, kb_y, 1, 1))

            # hands typing on keyboard: alternate positions
            left_hand = kb_x0 + max(1, kb_w//6) + (0 if i%2==0 else 1)
            right_hand = kb_x0 + kb_w - max(2, kb_w//6) - (0 if i%2==0 else 1)
            self._safe_set_px(s, left_hand, kb_y, self.palette['skin'])
            self._safe_set_px(s, right_hand, kb_y, self.palette['skin'])

            setup.append(s)
        return setup

    def _build_transition_frames(self):
        # short sit-down transition (6 frames) where a chair appears and avatar shifts down
        frames = []
        n = 6
        for i in range(n):
            s = self._make_canvas()
            # progressive breathe/down shift to simulate sitting
            breathe = 0
            # calculate downward shift: 0..3 pixels over frames
            down = int((i / (n - 1)) * 3)
            self._draw_base(s, breathe_offset=down, eyes_open=True)

            # draw a simple chair under the avatar that grows into view
            w, h = self.pw, self.ph
            chair_h = max(1, (i * 2) // 3)
            chair_y = h - chair_h - 2
            chair_x0 = max(1, w//4)
            chair_w = max(4, w - chair_x0*2)
            for yy in range(chair_h):
                for xx in range(chair_w):
                    px = chair_x0 + xx
                    py = chair_y + yy
                    if 0 <= px < w and 0 <= py < h:
                        # chair color: darker hood tone
                        s.fill((80, 40, 40), (px, py, 1, 1))

            frames.append(s)
        return frames

    def _safe_set_px(self, surf, x, y, col):
        if 0 <= x < surf.get_width() and 0 <= y < surf.get_height():
            surf.fill(col, (x, y, 1, 1))

    def _draw_base(self, surf, breathe_offset=0, eyes_open=True):
        p = self.palette
        w, h = self.pw, self.ph

        # Proportional layout so the avatar scales well for different pixel sizes
        head_w = max(6, int(w * 0.4))
        head_h = head_w
        head_x = (w - head_w) // 2
        head_y = max(1, int(h * 0.05)) + breathe_offset

        # Draw hood behind the head (slightly larger)
        hood_w = head_w + max(2, head_w // 3)
        hood_h = head_h + max(2, head_h // 3)
        hood_x = max(0, head_x - (hood_w - head_w)//2)
        hood_y = max(0, head_y - (hood_h - head_h)//2)
        for yy in range(hood_h):
            for xx in range(hood_w):
                px = hood_x + xx
                py = hood_y + yy
                if 0 <= px < w and 0 <= py < h:
                    # darker rim on hood edges
                    if xx in (0, hood_w-1) or yy in (0, hood_h-1):
                        self._set_px(surf, px, py, p['hood_dark'])
                    else:
                        self._set_px(surf, px, py, p['hood'])

        # Head (skin + hair top)
        for yy in range(head_h):
            for xx in range(head_w):
                px = head_x + xx
                py = head_y + yy
                if 0 <= px < w and 0 <= py < h:
                    # top row hair
                    if yy == 0 and 1 <= xx <= head_w-2:
                        self._set_px(surf, px, py, p['hair'])
                    else:
                        self._set_px(surf, px, py, p['skin'])

        # Eyes / blink
        eye_y = head_y + max(1, head_h // 3)
        eye_lx = head_x + max(1, head_w // 5)
        eye_rx = head_x + head_w - max(2, head_w // 5)
        if eyes_open:
            self._set_px(surf, eye_lx, eye_y, p['eye'])
            self._set_px(surf, eye_rx, eye_y, p['eye'])
        else:
            for ex in range(eye_lx, eye_rx+1):
                self._set_px(surf, ex, eye_y, p['hair'])

        # Mouth
        mouth_x = head_x + head_w // 2
        mouth_y = head_y + head_h - max(2, head_h // 4)
        self._set_px(surf, mouth_x, mouth_y, p['skin_shadow'])

        # Beard: fill a small area under the mouth to form a beard/chin
        beard_col = p.get('beard', (180, 140, 80))
        beard_height = max(1, head_h // 4)
        beard_width = max(2, head_w // 2)
        beard_x0 = head_x + (head_w - beard_width)//2
        for by in range(1, beard_height + 1):
            for bx in range(beard_width):
                self._set_px(surf, beard_x0 + bx, mouth_y + by, beard_col)

        # Body
        body_h = max(6, int(h * 0.35))
        body_w = max(6, int(w * 0.6))
        body_x = (w - body_w) // 2
        body_y = head_y + head_h
        for yy in range(body_h):
            for xx in range(body_w):
                px = body_x + xx
                py = body_y + yy
                if 0 <= px < w and 0 <= py < h:
                    # darker lower hem
                    if yy >= body_h - max(1, body_h//6):
                        self._set_px(surf, px, py, p['hood_dark'])
                    else:
                        self._set_px(surf, px, py, p['hood'])

        # Pocket accent
        pocket_w = max(2, body_w // 4)
        pocket_x = body_x + (body_w - pocket_w)//2
        pocket_y = body_y + max(1, body_h//3)
        for px in range(pocket_x, pocket_x + pocket_w):
            self._set_px(surf, px, pocket_y, p['trim'])

        # Legs
        leg_w = max(2, int(body_w * 0.3))
        leg_h = max(4, int(h * 0.18))
        leg_y = body_y + body_h
        left_leg_x = body_x + 1
        right_leg_x = body_x + body_w - leg_w - 1
        for yy in range(leg_h):
            for xx in range(leg_w):
                self._set_px(surf, left_leg_x + xx, leg_y + yy, p.get('pants', (30,30,40)))
                self._set_px(surf, right_leg_x + xx, leg_y + yy, p.get('pants', (30,30,40)))

        # Arms / hands: draw short sleeve rectangles and a visible hand pixel
        arm_w = max(2, body_w // 6)
        arm_h = max(3, body_h // 2)
        arm_y = body_y + max(1, body_h // 4)
        sleeve_col = p.get('hood')
        sleeve_dark = p.get('hood_dark')
        hand_col = p.get('skin')

        # left sleeve rectangle
        la_x = body_x - arm_w
        for yy in range(arm_h):
            for xx in range(arm_w):
                px = la_x + xx
                py = arm_y + yy
                if 0 <= px < w and 0 <= py < h:
                    # darker rim on outermost column
                    if xx == 0:
                        self._set_px(surf, px, py, sleeve_dark)
                    else:
                        self._set_px(surf, px, py, sleeve_col)

        # left hand (2x2 block slightly outwards)
        hand_ly = arm_y + arm_h - 1
        for hx in (la_x - 2, la_x - 1):
            for hy in (hand_ly - 1, hand_ly):
                self._safe_set_px(surf, hx, hy, hand_col)

        # right sleeve rectangle
        ra_x = body_x + body_w
        for yy in range(arm_h):
            for xx in range(arm_w):
                px = ra_x + xx
                py = arm_y + yy
                if 0 <= px < w and 0 <= py < h:
                    # darker rim on outermost column
                    if xx == arm_w - 1:
                        self._set_px(surf, px, py, sleeve_dark)
                    else:
                        self._set_px(surf, px, py, sleeve_col)

        # right hand (2x2 block)
        hand_ry = arm_y + arm_h - 1
        for hx in (ra_x + arm_w, ra_x + arm_w + 1):
            for hy in (hand_ry - 1, hand_ry):
                self._safe_set_px(surf, hx, hy, hand_col)

        # simple outer border (1px) to help readability
        outline = p['outline']
        for ox in range(w):
            self._set_px(surf, ox, 0, outline)
            self._set_px(surf, ox, h-1, outline)
        for oy in range(h):
            self._set_px(surf, 0, oy, outline)
            self._set_px(surf, w-1, oy, outline)

    def update(self):
        now = pygame.time.get_ticks()
        # advance frame for current state
        frames = self.animations.get(self.state, self.frames)
        if now - self.last >= self.anim_rate:
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.last = now

        # if there's a state end time, return to idle when elapsed
        if self.state_end_time is not None and now >= self.state_end_time:
            # if we just finished the sit transition, move into the longer setup scene
            if self.state == 'transition':
                # start the setup coding scene for a longer duration
                self.set_state('setup', duration_ms=6000)
            else:
                self.set_state('idle')

    def set_state(self, state: str, duration_ms: int | None = None):
        if state not in self.animations:
            return
        self.state = state
        self.frame_index = 0
        self.last = pygame.time.get_ticks()
        if duration_ms is not None:
            self.state_end_time = self.last + duration_ms
        else:
            self.state_end_time = None

    def draw(self, surface, topleft, size):
        """Draw current frame at topleft resized to 'size' (w, h).

        Uses nearest-neighbor scaling by using pygame.transform.scale (no smoothing).
        """
        frames = self.animations.get(self.state, self.frames)
        frame = frames[self.frame_index]
        tw, th = size
        # preserve aspect ratio to avoid stretching; scale to fit then center
        scale_w = tw / self.pw
        scale_h = th / self.ph
        scale = int(max(1, min(scale_w, scale_h)))
        new_w = self.pw * scale
        new_h = self.ph * scale
        scaled = pygame.transform.scale(frame, (new_w, new_h))
        # center inside target rect
        dx = topleft[0] + (tw - new_w) // 2
        dy = topleft[1] + (th - new_h) // 2
        surface.blit(scaled, (dx, dy))
