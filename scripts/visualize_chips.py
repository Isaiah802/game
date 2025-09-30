import os
import sys
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
# ensure project root on sys.path so imports like uno_game.* resolve when running from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pygame
from uno_game.cards.chips import draw_chip_stack

pygame.init()
# create surface
w, h = 600, 200
surface = pygame.Surface((w, h))
surface.fill((30, 120, 40))
font = pygame.font.SysFont('Arial', 18)

# sample stacks
counts = [3, 7, 25, 0, 12]
x = 20
y = 20
for c in counts:
    # draw name label
    label = font.render(f'chips: {c}', True, (240, 240, 240))
    surface.blit(label, (x, y))
    draw_chip_stack(surface, x + 120, y, c, chip_radius=12, max_display=8, font=font)
    y += 40

# save image
out = os.path.join(os.path.dirname(__file__), 'chips_preview.png')
try:
    pygame.image.save(surface, out)
    print('Saved preview to', out)
except Exception as e:
    print('Failed to save preview:', e)
finally:
    pygame.quit()
