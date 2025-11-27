"""Loading screen with backgammon board background and animated progress bar."""

import pygame
import time
import math


class LoadingScreen:
    """A loading screen with backgammon board background and progress animation."""
    
    def __init__(self, title: str = 'Loading...', subtitle: str = '', duration: float = 2.0):
        """Initialize the loading screen.
        
        Args:
            title: Main title text
            subtitle: Subtitle text (optional)
            duration: How long to display the loading screen in seconds
        """
        self.title = title
        self.subtitle = subtitle
        self.duration = duration
    
    def _draw_backgammon_board(self, screen: pygame.Surface):
        """Draw a procedural backgammon board background."""
        width, height = screen.get_size()
        
        # Background - dark green felt
        screen.fill((12, 80, 34))
        
        # Wooden frame
        frame_color = (101, 67, 33)
        frame_width = 40
        pygame.draw.rect(screen, frame_color, (0, 0, width, frame_width))  # top
        pygame.draw.rect(screen, frame_color, (0, height - frame_width, width, frame_width))  # bottom
        pygame.draw.rect(screen, frame_color, (0, 0, frame_width, height))  # left
        pygame.draw.rect(screen, frame_color, (width - frame_width, 0, frame_width, height))  # right
        
        # Inner playing area
        inner_left = frame_width
        inner_right = width - frame_width
        inner_top = frame_width
        inner_bottom = height - frame_width
        inner_width = inner_right - inner_left
        inner_height = inner_bottom - inner_top
        
        # Draw felt background
        felt_color = (20, 100, 45)
        pygame.draw.rect(screen, felt_color, (inner_left, inner_top, inner_width, inner_height))
        
        # Central bar
        bar_width = 30
        bar_x = inner_left + inner_width // 2 - bar_width // 2
        bar_color = (101, 67, 33)
        pygame.draw.rect(screen, bar_color, (bar_x, inner_top, bar_width, inner_height))
        
        # Draw triangular points (alternating colors)
        num_points_per_side = 6
        point_width = (inner_width - bar_width) // (num_points_per_side * 2)
        point_height = inner_height * 0.45
        
        tan_color = (210, 180, 140)
        brown_color = (139, 90, 43)
        
        # Top points (left side)
        for i in range(num_points_per_side):
            x = inner_left + i * point_width
            color = tan_color if i % 2 == 0 else brown_color
            points = [
                (x, inner_top),
                (x + point_width, inner_top),
                (x + point_width // 2, inner_top + point_height)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (0, 0, 0), points, 1)
        
        # Top points (right side)
        for i in range(num_points_per_side):
            x = bar_x + bar_width + i * point_width
            color = tan_color if i % 2 == 0 else brown_color
            points = [
                (x, inner_top),
                (x + point_width, inner_top),
                (x + point_width // 2, inner_top + point_height)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (0, 0, 0), points, 1)
        
        # Bottom points (left side)
        for i in range(num_points_per_side):
            x = inner_left + i * point_width
            color = brown_color if i % 2 == 0 else tan_color
            points = [
                (x, inner_bottom),
                (x + point_width, inner_bottom),
                (x + point_width // 2, inner_bottom - point_height)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (0, 0, 0), points, 1)
        
        # Bottom points (right side)
        for i in range(num_points_per_side):
            x = bar_x + bar_width + i * point_width
            color = brown_color if i % 2 == 0 else tan_color
            points = [
                (x, inner_bottom),
                (x + point_width, inner_bottom),
                (x + point_width // 2, inner_bottom - point_height)
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (0, 0, 0), points, 1)
    
    def run(self, screen: pygame.Surface):
        """Display the loading screen for the specified duration.
        
        Args:
            screen: The pygame surface to draw on
        """
        clock = pygame.time.Clock()
        start_time = time.time()
        
        # Fonts
        try:
            title_font = pygame.font.SysFont('Arial', 48, bold=True)
            subtitle_font = pygame.font.SysFont('Arial', 24)
        except Exception:
            title_font = pygame.font.Font(None, 48)
            subtitle_font = pygame.font.Font(None, 24)
        
        while time.time() - start_time < self.duration:
            # Handle events (allow quit)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
            
            # Calculate progress
            elapsed = time.time() - start_time
            progress = min(1.0, elapsed / self.duration)
            
            # Draw background
            self._draw_backgammon_board(screen)
            
            # Draw title
            title_surf = title_font.render(self.title, True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 60))
            screen.blit(title_surf, title_rect)
            
            # Draw subtitle
            if self.subtitle:
                subtitle_surf = subtitle_font.render(self.subtitle, True, (220, 220, 220))
                subtitle_rect = subtitle_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
                screen.blit(subtitle_surf, subtitle_rect)
            
            # Draw 3D progress bar
            bar_width = 400
            bar_height = 30
            bar_x = (screen.get_width() - bar_width) // 2
            bar_y = screen.get_height() // 2 + 40
            
            # Draw outer shadow/bevel (darker bottom/right edge)
            shadow_offset = 3
            pygame.draw.rect(screen, (30, 30, 30), 
                           (bar_x + shadow_offset, bar_y + shadow_offset, bar_width, bar_height), 
                           border_radius=15)
            
            # Background with gradient effect (darker at bottom)
            bg_surf = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            for i in range(bar_height):
                shade = 60 - int(i * 20 / bar_height)
                pygame.draw.line(bg_surf, (shade, shade, shade), (0, i), (bar_width, i))
            # Apply rounded corners
            bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(screen, (60, 60, 60), bg_rect, border_radius=15)
            screen.blit(bg_surf, (bar_x, bar_y), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Progress fill with 3D gradient
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                fill_surf = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
                # Gradient from bright at top to darker at bottom
                for i in range(bar_height):
                    ratio = i / bar_height
                    r = int(100 + (70 - 100) * ratio)
                    g = int(220 + (160 - 220) * ratio)
                    b = int(100 + (70 - 100) * ratio)
                    pygame.draw.line(fill_surf, (r, g, b), (0, i), (fill_width, i))
                
                # Draw fill with rounded corners
                fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
                pygame.draw.rect(screen, (100, 200, 100), fill_rect, border_radius=15)
                screen.blit(fill_surf, (bar_x, bar_y), special_flags=pygame.BLEND_RGBA_MULT)
                
                # Add glossy highlight on top third
                highlight = pygame.Surface((fill_width, bar_height // 3), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 60))
                screen.blit(highlight, (bar_x, bar_y))
            
            # Inner bevel (lighter top/left edge)
            pygame.draw.line(screen, (120, 120, 120), (bar_x + 15, bar_y + 2), (bar_x + bar_width - 15, bar_y + 2), 1)
            pygame.draw.line(screen, (120, 120, 120), (bar_x + 2, bar_y + 10), (bar_x + 2, bar_y + bar_height - 10), 1)
            
            # Border with subtle gradient
            pygame.draw.rect(screen, (180, 180, 180), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=15)
            
            # Draw backgammon-themed spinner (rotating dice)
            spinner_x = bar_x - 60
            spinner_y = bar_y + bar_height // 2
            spinner_size = 40
            rotation = elapsed * 180  # Rotate 180 degrees per second
            
            # Draw two dice spinning together (like backgammon dice)
            for offset_x in [-25, 25]:
                dice_x = spinner_x + offset_x
                dice_y = spinner_y
                
                # Create dice surface
                dice_surf = pygame.Surface((spinner_size, spinner_size), pygame.SRCALPHA)
                
                # Base die with shadow
                shadow_offset = 2
                pygame.draw.rect(dice_surf, (0, 0, 0, 60), 
                               (shadow_offset, shadow_offset, spinner_size - 4, spinner_size - 4), 
                               border_radius=6)
                
                # Die face (ivory/tan color for backgammon feel)
                pygame.draw.rect(dice_surf, (240, 230, 210), 
                               (0, 0, spinner_size - 4, spinner_size - 4), 
                               border_radius=6)
                
                # Die border
                pygame.draw.rect(dice_surf, (180, 150, 120), 
                               (0, 0, spinner_size - 4, spinner_size - 4), 
                               2, border_radius=6)
                
                # Draw pips (simple dots for cleaner look while spinning)
                pip_radius = 3
                pip_color = (80, 50, 30)
                center = spinner_size // 2 - 2
                
                # Draw center pip for visual interest
                pygame.draw.circle(dice_surf, pip_color, (center, center), pip_radius)
                
                # Rotate the dice
                angle = rotation + (180 if offset_x > 0 else 0)  # Counter-rotate for variety
                rotated = pygame.transform.rotate(dice_surf, angle)
                rotated_rect = rotated.get_rect(center=(dice_x, dice_y))
                screen.blit(rotated, rotated_rect)
            
            # Percentage text
            percent_text = f"{int(progress * 100)}%"
            percent_surf = subtitle_font.render(percent_text, True, (255, 255, 255))
            percent_rect = percent_surf.get_rect(center=(screen.get_width() // 2, bar_y + bar_height + 25))
            screen.blit(percent_surf, percent_rect)
            
            pygame.display.flip()
            clock.tick(60)
