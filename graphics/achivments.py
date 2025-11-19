"""Achievement popup notifications (Steam-style) displayed in the bottom-right.

Usage:
  from graphics.achivments import AchievementNotifier
  notifier = AchievementNotifier()
  # In your main loop: call notifier.update() and notifier.draw(screen)
  # When an achievement is unlocked:
  notifier.show("First Win", "Win your first round", image_path='assets/achieve1.png')

This file provides a small, dependency-free notifier using pygame only.
"""
import os
import time
import pygame
from typing import Optional, List

BASE_DIR = os.path.dirname(__file__)


class AchievementPopup:
	def __init__(self, title: str, subtitle: str = "", image: Optional[pygame.Surface] = None,
				 duration: float = 4.0):
		self.title = title
		self.subtitle = subtitle
		self.image = image
		self.duration = duration  # seconds visible including fades
		# Use pygame ticks if available, otherwise fallback to time.time()
		try:
			self.start_ms = pygame.time.get_ticks()
		except Exception:
			self.start_ms = int(time.time() * 1000)
		# animation timings (seconds)
		self.fade_in = 0.35
		self.fade_out = 0.6

	def elapsed(self) -> float:
		return (pygame.time.get_ticks() - self.start_ms) / 1000.0

	def alpha(self) -> int:
		e = self.elapsed()
		if e < self.fade_in:
			# fade in
			return int(255 * (e / max(1e-6, self.fade_in)))
		elif e > (self.duration - self.fade_out):
			# fade out
			t = (e - (self.duration - self.fade_out)) / max(1e-6, self.fade_out)
			return int(255 * max(0.0, 1.0 - t))
		else:
			return 255

	def is_expired(self) -> bool:
		return self.elapsed() > self.duration


class AchievementNotifier:
	"""Manage and render stacked achievement popups in the bottom-right.

	Call `update()` each frame (or once per loop) and `draw(surface)` to render.
	Use `show(title, subtitle, image_path)` to enqueue a popup.
	"""

	PADDING = 12
	THUMB = 64
	WIDTH = 360
	HEIGHT = 80

	def __init__(self):
		self.queue: List[AchievementPopup] = []
		# Defer font creation until pygame.font is initialized
		self.font_title = None
		self.font_sub = None

	def ensure_fonts(self):
		"""Create font objects if not already created. Safe to call before pygame.init()."""
		if self.font_title and self.font_sub:
			return
		try:
			if not pygame.font.get_init():
				pygame.font.init()
			self.font_title = pygame.font.SysFont('Arial', 18, bold=True)
			self.font_sub = pygame.font.SysFont('Arial', 14)
		except Exception:
			# Last-resort: create dummy font-like placeholders (render will fail gracefully)
			self.font_title = None
			self.font_sub = None

	def load_image(self, path: Optional[str]) -> Optional[pygame.Surface]:
		if not path:
			return None
		# resolve relative to project base if not absolute
		if not os.path.isabs(path):
			cand = os.path.join(BASE_DIR, '..', path)
			if os.path.exists(cand):
				path = cand
		try:
			img = pygame.image.load(path).convert_alpha()
			img = pygame.transform.smoothscale(img, (self.THUMB, self.THUMB))
			return img
		except Exception:
			return None

	def show(self, title: str, subtitle: str = "", image_path: Optional[str] = None, duration: float = 4.0):
		# ensure fonts ready for rendering when popup is created
		self.ensure_fonts()
		img = self.load_image(image_path) if image_path else None
		p = AchievementPopup(title, subtitle, img, duration)
		self.queue.append(p)

	def update(self):
		# Remove expired popups
		self.queue = [p for p in self.queue if not p.is_expired()]

	def draw(self, surface: pygame.Surface):
		# Ensure fonts exist before drawing
		self.ensure_fonts()
		# Draw stacked from bottom-right upwards
		sw, sh = surface.get_size()
		x = sw - self.WIDTH - self.PADDING
		y = sh - self.PADDING

		# draw last in queue at bottom
		for popup in reversed(self.queue):
			y -= self.HEIGHT
			alpha = popup.alpha()

			# background surface per-popup to allow fade
			surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
			# semi-opaque dark background
			surf.fill((20, 20, 30, int(220 * (alpha / 255))))

			# draw thumb
			img_x = 10
			if popup.image:
				img = popup.image.copy()
				img.set_alpha(alpha)
				surf.blit(img, (img_x, (self.HEIGHT - self.THUMB) // 2))
			else:
				# placeholder box
				box = pygame.Surface((self.THUMB, self.THUMB), pygame.SRCALPHA)
				box.fill((80, 120, 200, alpha))
				surf.blit(box, (img_x, (self.HEIGHT - self.THUMB) // 2))

			# draw text
			tx = img_x + self.THUMB + 12
			ty = 12
			title_surf = self.font_title.render(popup.title, True, (255, 255, 255))
			title_surf.set_alpha(alpha)
			surf.blit(title_surf, (tx, ty))

			if popup.subtitle:
				sub_surf = self.font_sub.render(popup.subtitle, True, (200, 200, 200))
				sub_surf.set_alpha(alpha)
				surf.blit(sub_surf, (tx, ty + 28))

			# border
			pygame.draw.rect(surf, (120, 120, 140, int(120 * (alpha / 255))), surf.get_rect(), 1)

			# finally blit the composed popup onto the target surface
			surface.blit(surf, (x, y))

			y -= 8  # small gap between stacked popups


# Convenience singleton used by game code
notifier = AchievementNotifier()

