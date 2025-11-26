from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton
from direct.interval.IntervalGlobal import LerpColorScaleInterval
from panda3d.core import OnscreenImage, TransparencyAttrib
import time, os

class IntroScreen:
    """Panda3D-based intro/splash screen with fade-in, background, and tips."""
    def __init__(self, base, title='Zanzibar', subtitle='', duration=2.5, tips=None):
        self.base = base
        self.title = title
        self.subtitle = subtitle
        self.duration = duration
        self.tips = tips or [
            "Tip: Press F to toggle fullscreen",
            "Tip: Press Space to roll dice",
            "Tip: You can change music in Change Song",
            "Tip: Add at least 2 players to start",
            "Tip: Press Esc to open the menu",
        ]
        self.bg_image_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'ui', 'casino_background.jpg')

    def run(self):
        # Fade-in effect
        self.base.render.setColorScale(0, 0, 0, 1)
        fade_in = LerpColorScaleInterval(self.base.render, 1.2, (1, 1, 1, 1))
        fade_in.start()

        # Show background image
        bg_img = None
        if os.path.exists(self.bg_image_path):
            bg_img = OnscreenImage(image=self.bg_image_path, pos=(0, 0, 0), scale=(1.78, 1, 1), parent=self.base.render2d)
            bg_img.setTransparency(TransparencyAttrib.MAlpha)

        # Title and subtitle
        title_lbl = DirectLabel(text=self.title, scale=0.13, pos=(0, 0, 0.55), text_fg=(1, 0.85, 0.2, 1), frameColor=(0,0,0,0), parent=self.base.aspect2d)
        subtitle_lbl = DirectLabel(text=self.subtitle, scale=0.07, pos=(0, 0, 0.42), text_fg=(0.95, 0.95, 1, 1), frameColor=(0,0,0,0), parent=self.base.aspect2d)

        # Tip label
        tip_lbl = DirectLabel(text=self.tips[0], scale=0.05, pos=(0, 0, -0.7), text_fg=(0.9, 0.3, 0.3, 1), frameColor=(0,0,0,0), parent=self.base.aspect2d)

        # Skip button (appears after min time)
        skip_btn = None
        min_time = 1.0
        start_time = time.time()
        while time.time() - start_time < self.duration:
            elapsed = time.time() - start_time
            # Show skip button after min_time
            if skip_btn is None and elapsed > min_time:
                skip_btn = DirectButton(text='Skip', scale=0.06, pos=(0.8, 0, -0.8), frameColor=(0.2,0.2,0.3,1), text_fg=(0.95,0.95,0.95,1), parent=self.base.aspect2d, command=self._skip)
            self.base.taskMgr.step()
            # Cycle tips
            tip_lbl['text'] = self.tips[int((elapsed*1.5)%len(self.tips))]
            if hasattr(self, '_skipped') and self._skipped:
                break
        # Cleanup
        if bg_img: bg_img.removeNode()
        title_lbl.destroy()
        subtitle_lbl.destroy()
        tip_lbl.destroy()
        if skip_btn: skip_btn.destroy()

    def _skip(self):
        self._skipped = True
                steps = max(10, int(self.duration * 10))
                for i in range(steps):
                    time.sleep(max(0.01, self.duration / steps))
                    cb((i + 1) / steps)
            t = threading.Thread(target=lambda: (fake_loader(progress_cb), state.update({'done': True})), daemon=True)
            t.start()

        running = True
        tip_idx = 0
        last_tip = time.time()
        spinner_angle = 0.0

        while running:
            now = time.time()
            elapsed = now - start
            # progress fraction (prefer real loader progress when available)
            frac = state['progress']

            # Panda3D DirectGui input/callbacks will be handled here.
                        except Exception:
                            pass

            # draw background with gradient
            if bg_image:
                # Draw semi-transparent gradient over the background image
                screen.blit(bg_image, (0, 0))
                gradient_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                for y in range(height):
                    progress = y / height
                    color = [
                        int(self.gradient_top[i] * (1 - progress) + self.gradient_bottom[i] * progress)
                        for i in range(3)
                    ] + [150]  # Semi-transparent overlay
                    pygame.draw.line(gradient_surf, color, (0, y), (width, y))
                screen.blit(gradient_surf, (0, 0))
            else:
                screen.fill(self.bg_color)
                # Draw a subtle gradient
                for y in range(height):
                    progress = y / height
                    color = [
                        int(self.gradient_top[i] * (1 - progress) + self.gradient_bottom[i] * progress)
                        for i in range(3)
                    ]
                    pygame.draw.line(screen, color, (0, y), (width, y))

            # Animated title glow effect
            glow = abs(math.sin(time.time() * 2)) * 0.3 + 0.7
            title_color = [int(c * glow) for c in self.title_color]
            title_surf = font_title.render(self.title, True, title_color)
            tr = title_surf.get_rect(center=(width // 2, int(height * 0.35)))
            
            # Add shadow to title
            shadow_surf = font_title.render(self.title, True, (0, 0, 0))
            shadow_rect = shadow_surf.get_rect(center=(tr.centerx + 2, tr.centery + 2))
            screen.blit(shadow_surf, shadow_rect)
            screen.blit(title_surf, tr)

            # subtitle with fade effect
            if self.subtitle:
                sub_alpha = int(255 * (abs(math.sin(time.time() * 1.5)) * 0.2 + 0.8))
                sub_surf = font_sub.render(self.subtitle, True, self.subtitle_color)
                    # TODO: Replace with Panda3D texture/OnscreenImage drawing
                    pass
                sub_surf.set_alpha(sub_alpha)
                sr = sub_surf.get_rect(center=(width // 2, tr.bottom + 24))
                screen.blit(sub_surf, sr)

            # Modern progress bar with glow
            bar_w = int(width * 0.5)
            bar_h = 18
            bar_x = (width - bar_w) // 2
            bar_y = sr.bottom + 24 if self.subtitle else tr.bottom + 24
            
            # Draw progress bar background with rounded corners
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=9)
            
            # Draw progress with gradient and glow
            if frac > 0:
                progress_width = int((bar_w - 4) * frac)
                progress_surf = pygame.Surface((progress_width, bar_h - 4), pygame.SRCALPHA)
                for x in range(progress_width):
                    progress = x / progress_width
                    glow_intensity = abs(math.sin(time.time() * 3 + x * 0.1)) * 0.3 + 0.7
                    color = [int(c * glow_intensity) for c in self.accent_color]
                    pygame.draw.line(progress_surf, color, (x, 0), (x, bar_h - 4))
                screen.blit(progress_surf, (bar_x + 2, bar_y + 2))

            # spinner (animated)
            spinner_center = (bar_x + bar_w + 48, bar_y + bar_h // 2)
            spinner_radius = 10
            spinner_steps = 8
            spinner_angle += 0.08
            for i in range(spinner_steps):
                a = spinner_angle + (i * (2 * math.pi / spinner_steps))
                sx = spinner_center[0] + math.cos(a) * (spinner_radius + 6)
                sy = spinner_center[1] + math.sin(a) * (spinner_radius + 6)
                fade = int(255 * ((i + 1) / spinner_steps))
                col = (fade, fade, fade)
                pygame.draw.circle(screen, col, (int(sx), int(sy)), 4)

            # tips
            if now - last_tip > 3.0:
                tip_idx = (tip_idx + 1) % len(self.tip_list)
                last_tip = now
            tip_surf = font_small.render(self.tip_list[tip_idx], True, (200, 200, 200))
            tip_r = tip_surf.get_rect(center=(width // 2, bar_y + bar_h + 22))
            screen.blit(tip_surf, tip_r)

            # percent
            pct_surf = font_small.render(f"Loading... {int(frac * 100)}%", True, (220, 220, 220))
            screen.blit(pct_surf, (bar_x, bar_y - 26))

            # Enhanced error display
            if state.get('error'):
                err = state['error']
                # Create error background
                error_height = 60
                error_y = bar_y + bar_h + 30
                error_surface = pygame.Surface((width * 0.8, error_height), pygame.SRCALPHA)
                pygame.draw.rect(error_surface, (255, 0, 0, 50), error_surface.get_rect(), border_radius=10)
                
                # Error icon (X symbol)
                icon_size = 24
                icon_x = 20
                pygame.draw.line(error_surface, (255, 100, 100), 
                               (icon_x, error_height//2 - icon_size//2),
                               (icon_x + icon_size, error_height//2 + icon_size//2), 3)
                pygame.draw.line(error_surface, (255, 100, 100),
                               (icon_x, error_height//2 + icon_size//2),
                               (icon_x + icon_size, error_height//2 - icon_size//2), 3)
                
                # Error message with word wrap
                words = f"Error: {err}".split()
                lines = []
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    test_surface = font_small.render(test_line, True, (255, 120, 120))
                    if test_surface.get_width() < width * 0.7:
                        current_line.append(word)
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Render error message lines
                for i, line in enumerate(lines):
                    error_text = font_small.render(line, True, (255, 120, 120))
                    error_surface.blit(error_text, (icon_x + icon_size + 20, 10 + i * 20))
                
                # Add pulsing effect to error message
                error_alpha = int(255 * (abs(math.sin(time.time() * 2)) * 0.2 + 0.8))
                error_surface.set_alpha(error_alpha)
                
                # Display error surface
                screen.blit(error_surface, ((width - error_surface.get_width())//2, error_y))
                
                # Retry button
                retry_text = font_sub.render("Press R to retry", True, (255, 200, 200))
                retry_rect = retry_text.get_rect(center=(width//2, error_y + error_height + 20))
                screen.blit(retry_text, retry_rect)

            pygame.display.flip()
            clock.tick(60)

            # fade SFX near the end if audio provided
            if sound_obj is not None and sfx_channel is not None:
                time_left = max(0.0, self.duration - elapsed)
                if time_left <= fade_duration:
                    frac_f = max(0.0, time_left / fade_duration)
                    try:
                        sound_obj.set_volume(frac_f * audio_manager.get_sfx_volume())
                    except Exception:
                        pass

            # break when loader is done and a minimal display time has passed
            if state['done'] and elapsed >= min(self.duration, 0.25):
                try:
                    if sfx_channel is not None:
                        sfx_channel.stop()
                except Exception:
                    pass
                break
