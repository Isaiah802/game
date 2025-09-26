import pygame
from typing import Optional


class AudioSettingsMenu:
    """Simple audio settings menu to adjust music and sfx volumes.

    Usage:
        menu = AudioSettingsMenu(screen, audio_manager)
        menu.run()  # updates audio_manager in-place
    """

    def __init__(self, screen: pygame.Surface, audio_manager, width=800, height=600):
        self.screen = screen
        self.am = audio_manager
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        # volumes stored 0.0-1.0
        try:
            self.music_vol = float(self.am.get_music_volume())
        except Exception:
            self.music_vol = 0.5
        try:
            self.sfx_vol = float(self.am.get_sfx_volume())
        except Exception:
            self.sfx_vol = 1.0

    def draw(self):
        self.screen.fill((40, 30, 30))
        title = self.title_font.render('Audio Settings', True, (255, 255, 255))
        tr = title.get_rect(center=(self.width // 2, 60))
        self.screen.blit(title, tr)

        mv = self.font.render(f'Music Volume: {int(self.music_vol*100)}%', True, (255, 255, 255))
        sv = self.font.render(f'SFX Volume: {int(self.sfx_vol*100)}%', True, (255, 255, 255))
        self.screen.blit(mv, (80, 140))
        self.screen.blit(sv, (80, 200))

        instr = self.font.render('Use Left/Right to change Music, A/D to change SFX. Enter to save, Esc to cancel', True, (200, 200, 200))
        ir = instr.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(instr, ir)

        pygame.display.flip()

    def run(self) -> Optional[dict]:
        running = True
        result = None
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.music_vol = max(0.0, self.music_vol - 0.05)
                        try:
                            self.am.set_music_volume(self.music_vol)
                        except Exception:
                            pass
                    elif event.key == pygame.K_RIGHT:
                        self.music_vol = min(1.0, self.music_vol + 0.05)
                        try:
                            self.am.set_music_volume(self.music_vol)
                        except Exception:
                            pass
                    elif event.key == pygame.K_a:
                        self.sfx_vol = max(0.0, self.sfx_vol - 0.05)
                        try:
                            self.am.set_sfx_volume(self.sfx_vol)
                        except Exception:
                            pass
                    elif event.key == pygame.K_d:
                        self.sfx_vol = min(1.0, self.sfx_vol + 0.05)
                        try:
                            self.am.set_sfx_volume(self.sfx_vol)
                        except Exception:
                            pass
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        # save and exit
                        result = {'music_volume': self.music_vol, 'sfx_volume': self.sfx_vol}
                        running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            self.draw()
            self.clock.tick(60)

        return result
