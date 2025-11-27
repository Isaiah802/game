"""UI utility functions for transitions, confirmations, and visual effects."""

import pygame
import time


def fade_transition(screen: pygame.Surface, duration: float = 0.5, fade_out: bool = True):
    """Create a smooth fade transition effect.
    
    Args:
        screen: The pygame surface to fade
        duration: How long the fade should take in seconds
        fade_out: If True, fade to black. If False, fade from black.
    """
    clock = pygame.time.Clock()
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill((0, 0, 0))
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        progress = elapsed / duration
        
        if fade_out:
            alpha = int(255 * progress)
        else:
            alpha = int(255 * (1 - progress))
        
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def show_confirmation_dialog(screen: pygame.Surface, message: str, 
                            title: str = "Confirm") -> bool:
    """Show a confirmation dialog with Yes/No options.
    
    Args:
        screen: The pygame surface to draw on
        message: The confirmation message to display
        title: The dialog title
        
    Returns:
        True if user confirmed, False if cancelled
    """
    font_title = pygame.font.SysFont('Arial', 32, bold=True)
    font_msg = pygame.font.SysFont('Arial', 20)
    font_btn = pygame.font.SysFont('Arial', 24)
    
    # Dialog dimensions
    dialog_width = 500
    dialog_height = 250
    dialog_x = (screen.get_width() - dialog_width) // 2
    dialog_y = (screen.get_height() - dialog_height) // 2
    
    # Button dimensions
    btn_width = 120
    btn_height = 50
    btn_y = dialog_y + dialog_height - 80
    yes_btn_x = dialog_x + dialog_width // 2 - btn_width - 20
    no_btn_x = dialog_x + dialog_width // 2 + 20
    
    yes_rect = pygame.Rect(yes_btn_x, btn_y, btn_width, btn_height)
    no_rect = pygame.Rect(no_btn_x, btn_y, btn_width, btn_height)
    
    # Capture the current screen
    background = screen.copy()
    
    clock = pygame.time.Clock()
    selected = None  # None, 'yes', or 'no'
    
    while selected is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    if yes_rect.collidepoint(mx, my):
                        selected = 'yes'
                    elif no_rect.collidepoint(mx, my):
                        selected = 'no'
        
        # Draw darkened background
        screen.blit(background, (0, 0))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw dialog box
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        
        # Shadow
        shadow_rect = dialog_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=15)
        
        # Main box
        pygame.draw.rect(screen, (40, 40, 50), dialog_rect, border_radius=15)
        pygame.draw.rect(screen, (212, 175, 55), dialog_rect, 3, border_radius=15)
        
        # Title
        title_surf = font_title.render(title, True, (255, 220, 80))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, dialog_y + 40))
        screen.blit(title_surf, title_rect)
        
        # Message (word wrap)
        words = message.split(' ')
        lines = []
        current_line = []
        max_width = dialog_width - 40
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font_msg.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        msg_y = dialog_y + 90
        for line in lines:
            msg_surf = font_msg.render(line, True, (220, 220, 220))
            msg_rect = msg_surf.get_rect(center=(screen.get_width() // 2, msg_y))
            screen.blit(msg_surf, msg_rect)
            msg_y += 30
        
        # Buttons
        mx, my = pygame.mouse.get_pos()
        
        # Yes button
        yes_hover = yes_rect.collidepoint(mx, my)
        yes_color = (80, 180, 80) if yes_hover else (60, 140, 60)
        pygame.draw.rect(screen, yes_color, yes_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 220, 100), yes_rect, 2, border_radius=10)
        yes_text = font_btn.render("Yes", True, (255, 255, 255))
        yes_text_rect = yes_text.get_rect(center=yes_rect.center)
        screen.blit(yes_text, yes_text_rect)
        
        # No button
        no_hover = no_rect.collidepoint(mx, my)
        no_color = (180, 60, 60) if no_hover else (140, 40, 40)
        pygame.draw.rect(screen, no_color, no_rect, border_radius=10)
        pygame.draw.rect(screen, (220, 80, 80), no_rect, 2, border_radius=10)
        no_text = font_btn.render("No", True, (255, 255, 255))
        no_text_rect = no_text.get_rect(center=no_rect.center)
        screen.blit(no_text, no_text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    return selected == 'yes'


def show_tooltip(screen: pygame.Surface, text: str, x: int, y: int, 
                 max_width: int = 300, padding: int = 10):
    """Draw a tooltip at the specified position.
    
    Args:
        screen: The pygame surface to draw on
        text: The tooltip text
        x: X position (will adjust to stay on screen)
        y: Y position (will adjust to stay on screen)
        max_width: Maximum width of tooltip
        padding: Internal padding
    """
    font = pygame.font.SysFont('Arial', 16)
    
    # Word wrap
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width - padding * 2:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    # Calculate tooltip dimensions
    line_height = font.get_linesize()
    tooltip_width = max(font.size(line)[0] for line in lines) + padding * 2
    tooltip_height = len(lines) * line_height + padding * 2
    
    # Adjust position to stay on screen
    if x + tooltip_width > screen.get_width():
        x = screen.get_width() - tooltip_width - 5
    if y + tooltip_height > screen.get_height():
        y = y - tooltip_height - 10
    
    # Draw tooltip
    tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
    
    # Shadow
    shadow_rect = tooltip_rect.copy()
    shadow_rect.x += 3
    shadow_rect.y += 3
    shadow_surf = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
    shadow_surf.fill((0, 0, 0, 100))
    screen.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
    
    # Background
    pygame.draw.rect(screen, (50, 50, 60), tooltip_rect, border_radius=8)
    pygame.draw.rect(screen, (180, 180, 200), tooltip_rect, 2, border_radius=8)
    
    # Text
    text_y = y + padding
    for line in lines:
        line_surf = font.render(line, True, (255, 255, 255))
        screen.blit(line_surf, (x + padding, text_y))
        text_y += line_height


def create_particle_burst(x: int, y: int, count: int = 30) -> list:
    """Create a particle burst effect for celebrations.
    
    Args:
        x: X position of burst origin
        y: Y position of burst origin
        count: Number of particles to create
        
    Returns:
        List of particle dictionaries with position, velocity, color, life
    """
    import random
    import math
    
    particles = []
    colors = [
        (255, 215, 0),  # Gold
        (255, 140, 0),  # Orange
        (255, 69, 0),   # Red-Orange
        (255, 255, 255),  # White
        (255, 192, 203),  # Pink
    ]
    
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 300)
        particles.append({
            'x': x,
            'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed - 100,  # Bias upward
            'color': random.choice(colors),
            'life': random.uniform(1.0, 2.0),
            'size': random.randint(3, 7),
            'gravity': random.uniform(200, 400)
        })
    
    return particles


def update_and_draw_particles(screen: pygame.Surface, particles: list, dt: float) -> list:
    """Update and draw particle effects, removing dead particles.
    
    Args:
        screen: The pygame surface to draw on
        particles: List of particle dictionaries
        dt: Delta time in seconds
        
    Returns:
        Updated list with dead particles removed
    """
    alive_particles = []
    
    for p in particles:
        # Update
        p['life'] -= dt
        if p['life'] <= 0:
            continue
        
        p['x'] += p['vx'] * dt
        p['y'] += p['vy'] * dt
        p['vy'] += p['gravity'] * dt  # Apply gravity
        
        # Draw with fade based on life
        alpha = int(255 * (p['life'] / 2.0))
        alpha = max(0, min(255, alpha))
        
        surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
        color_with_alpha = (*p['color'], alpha)
        pygame.draw.circle(surf, color_with_alpha, (p['size'], p['size']), p['size'])
        screen.blit(surf, (int(p['x'] - p['size']), int(p['y'] - p['size'])))
        
        alive_particles.append(p)
    
    return alive_particles
