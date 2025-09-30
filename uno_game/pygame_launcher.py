import os
import sys
import subprocess
import pygame

from ui.start_menu import StartMenu


def run_menu():
    pygame.init()
    WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Game - Launcher")

    menu = StartMenu(screen, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    while True:
        choice = menu.run()
        if choice == 'play':
            # Placeholder: no full game implemented here
            print('Play chosen (no game)')
            continue
        elif choice == 'dice':
            # Launch the turtle dice demo in a separate process so it has its own
            # event loop and windowing; use the same Python executable.
            script_path = os.path.join(os.path.dirname(__file__), 'main.py')
            try:
                subprocess.Popen([sys.executable, script_path])
            except Exception as e:
                print('Failed to launch dice demo:', e)
            continue
        elif choice == 'change_song':
            # Existing flow for changing songs is handled elsewhere; return to menu
            print('Change song selected (no-op in launcher)')
            continue
        elif choice == 'settings':
            print('Settings selected (no-op in launcher)')
            continue
        elif choice == 'quit':
            break


if __name__ == '__main__':
    run_menu()
