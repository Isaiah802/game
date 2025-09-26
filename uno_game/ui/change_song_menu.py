import os
import pygame
from typing import List, Optional


class ChangeSongMenu:
    """Simple menu to pick a music file from the audio folder.

    Usage:
        menu = ChangeSongMenu(screen, audio_folder)
        choice = menu.run()  # returns filename or None
    """

    def __init__(self, screen: pygame.Surface, audio_folder: str, width=800, height=600, audio_manager=None):
        self.screen = screen
        # If an AudioManager was provided, prefer its songs_folder
        self.audio = audio_manager
        if audio_manager is not None and hasattr(audio_manager, 'songs_folder'):
            self.audio_folder = audio_manager.songs_folder
        else:
            self.audio_folder = audio_folder
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.files: List[str] = []
        self.selected = 0
        # optional AudioManager for live preview (may have been set earlier)
        if getattr(self, 'audio', None) is None:
            self.audio = audio_manager
        self._last_preview_index = None
        self._load_files()

    def _load_files(self):
        if not os.path.exists(self.audio_folder):
            self.files = []
            return
        self.files = [f for f in os.listdir(self.audio_folder) if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
        self.files.sort()
        if not self.files:
            self.selected = 0

    def draw(self):
        self.screen.fill((25, 25, 50))
        title = self.title_font.render('Select Music', True, (255, 255, 255))
        tr = title.get_rect(center=(self.width // 2, 60))
        self.screen.blit(title, tr)

        start_y = 120
        gap = 40
        for i, fname in enumerate(self.files):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            txt = self.font.render(fname, True, color)
            self.screen.blit(txt, (80, start_y + i * gap))

        if not self.files:
            msg = self.font.render('No music files found in folder.', True, (200, 200, 200))
            self.screen.blit(msg, (80, 140))

        instr = self.font.render('Up/Down to select, Enter to play & return, Esc to cancel', True, (180, 180, 180))
        ir = instr.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(instr, ir)

        pygame.display.flip()

    def run(self) -> Optional[str]:
        running = True
        result: Optional[str] = None
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if self.files:
                            self.selected = (self.selected - 1) % len(self.files)
                            # preview new selection
                            self._maybe_preview()
                    elif event.key == pygame.K_DOWN:
                        if self.files:
                            self.selected = (self.selected + 1) % len(self.files)
                            # preview new selection
                            self._maybe_preview()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if self.files:
                            result = self.files[self.selected]
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            # Also preview if selection changed via other means
            self._maybe_preview()
            self.draw()
            self.clock.tick(60)

        return result

    def _maybe_preview(self):
        """Play a short preview when the highlighted selection changes."""
        if self.audio is None:
            return
        if not self.files:
            return
        if self._last_preview_index == self.selected:
            return
        self._last_preview_index = self.selected
        fname = self.files[self.selected]
        try:
            # play non-looping preview
            self.audio.play_music(fname, loop=False, volume=0.6)
        except Exception:
            pass
