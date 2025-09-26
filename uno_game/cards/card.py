import turtle
import random
import typing


def draw_uno_card_pygame(surface, x, y, card, card_width=80, card_height=120):
    """Draw a single UNO-style card onto a pygame surface.

    This helper mirrors the turtle `draw_uno_card` visuals but uses pygame.
    It's kept here so callers can import drawing functionality from this module
    rather than duplicating code in `main.py`.
    """
    try:
        import pygame
    except Exception:
        raise RuntimeError("pygame is required for draw_uno_card_pygame")

    color_map = {
        'Red': (255, 85, 85),
        'Yellow': (255, 170, 0),
        'Green': (85, 170, 85),
        'Blue': (85, 85, 255),
        'Wild': (0, 0, 0),
    }
    card_color = color_map.get(card.get('color'), (128, 128, 128))

    rect = pygame.Rect(x, y, card_width, card_height)
    pygame.draw.rect(surface, card_color, rect)
    pygame.draw.rect(surface, (0, 0, 0), rect, 2)

    text_color = (0, 0, 0) if card.get('color') == 'Yellow' else (255, 255, 255)
    font = pygame.font.SysFont('Arial', 24, bold=True)
    text_surface = font.render(str(card.get('type')), True, text_color)
    text_rect = text_surface.get_rect(center=(x + card_width / 2, y + card_height / 2))
    surface.blit(text_surface, text_rect)



def create_uno_deck():
    """Creates and returns a simple list of UNO card dictionaries."""
    deck = []
    colors = ['Red', 'Yellow', 'Green', 'Blue']
    types = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw Two']

    # Standard colored cards
    for color in colors:
        deck.append({'color': color, 'type': '0'})  # One '0' of each color
        for card_type in types[1:]:  # Two of each 1-9, Skip, Reverse, Draw Two
            for _ in range(2):
                deck.append({'color': color, 'type': card_type})

    # Wild cards
    for _ in range(4):
        deck.append({'color': 'Wild', 'type': 'Wild'})
        deck.append({'color': 'Wild', 'type': 'Wild Draw Four'})  # Assuming these are part of the basic 4 wilds

    return deck


# --- Refined draw_uno_card function ---
def draw_uno_card(pen, x, y, card):
    """
    Draws a single UNO card at a specific location using a given turtle pen.
    - pen: The turtle object to use for drawing.
    - x, y: The bottom-left corner coordinates to start drawing from.
    - card: A dictionary like {'color': 'Blue', 'type': '7'}.
    """
    card_width = 80
    card_height = 120

    # --- Map game colors to screen colors ---
    color_map = {
        'Red': '#FF5555',
        'Yellow': '#FFAA00',
        'Green': '#55AA55',
        'Blue': '#5555FF',
        'Wild': 'black'  # Wild cards are black
    }
    card_color = color_map.get(card['color'], 'grey')  # Default to grey if color not found

    pen.penup()
    pen.goto(x, y)  # Move to the bottom-left corner of where the card should be
    pen.pendown()

    pen.color('black', card_color)  # Outline is black, fill is card's color
    pen.begin_fill()
    for _ in range(2):
        pen.forward(card_width)
        pen.left(90)
        pen.forward(card_height)
        pen.left(90)
    pen.end_fill()
    pen.penup()

    # --- Write the card number or symbol in the center ---
    text_color = "white" if card['color'] != 'Yellow' else 'black'  # Black text on yellow cards
    pen.color(text_color)

    # Position text in the center of the card
    text_x = x + (card_width / 2)
    text_y = y + (card_height / 2) - 15  # Adjust Y for text vertical alignment

    pen.goto(text_x, text_y)
    pen.write(card['type'], align="center", font=("Arial", 20, "bold"))


if __name__ == "__main__":
    # --- Main Script (turtle demo) ---
    screen = turtle.Screen()
    screen.setup(width=900, height=600)
    screen.bgcolor("darkgreen")
    screen.title("UNO Cards - Improved")
    screen.tracer(0)  # Turn off automatic screen updates for faster drawing

    # Create a single turtle pen for all drawing operations
    main_pen = turtle.Turtle()
    main_pen.hideturtle()
    main_pen.speed(0)  # Max speed

    # Create a deck of cards and shuffle it
    full_deck = create_uno_deck()
    random.shuffle(full_deck)

    # Draw 10 random cards from the deck in two neat rows
    card_spacing_x = 95
    card_spacing_y = 140  # Height + some space

    start_x_top_row = -350
    start_y_top_row = 100

    start_x_bottom_row = -350
    start_y_bottom_row = -50

    print(f"Drawing {min(len(full_deck), 10)} cards...")

    for i in range(10):  # Let's draw 10 cards to fill the display
        if not full_deck:
            print("No more cards in the deck to draw.")
            break

        card_to_draw = full_deck.pop()

        if i < 5:
            # First row
            card_x = start_x_top_row + (i * card_spacing_x)
            card_y = start_y_top_row
        else:
            # Second row
            card_x = start_x_bottom_row + ((i - 5) * card_spacing_x)
            card_y = start_y_bottom_row

        draw_uno_card(main_pen, card_x, card_y, card_to_draw)

    screen.update()  # Manually update the screen to show all drawings
    screen.exitonclick()