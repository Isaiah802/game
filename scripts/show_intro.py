import time
import pygame
import sys

from uno_game.ui.intro_screen import IntroScreen


def fake_loader(cb):
    # simulate a loading process
    for i in range(100):
        time.sleep(0.02)
        try:
            cb((i + 1) / 100.0)
        except Exception:
            pass


def main():
    pygame.init()
    size = (1280, 720)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('IntroScreen Preview')

    intro = IntroScreen(title='Zanzibar', subtitle='A Dice Game by I paid $1,152.60 to have this team name', duration=4.0, force_draw_casino=True)

    try:
        intro.run(screen, audio_manager=None, load_work=fake_loader)
    except Exception as e:
        print('Intro run failed:', e)
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
