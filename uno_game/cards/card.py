import random
import turtle


# --- CARD DRAWING FUNCTION (No changes here) ---
def draw_uno_card(x, y, card):
    """
    Draws a visual representation of an UNO card on the screen.
    - x, y: The bottom-left corner coordinates to start drawing from.
    - card: A dictionary like {'color': 'Blue', 'type': '7'}.
    """
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.penup()

    color_map = {'Red': '#FF5555', 'Yellow': '#FFAA00', 'Green': '#55AA55', 'Blue': '#5555FF', 'Wild': 'black'}
    card_color = color_map.get(card['color'], 'black')

    pen.goto(x, y)
    pen.pendown()
    pen.color('black', card_color)
    pen.begin_fill()
    for _ in range(2):
        pen.forward(100)
        pen.left(90)
        pen.forward(150)
        pen.left(90)
    pen.end_fill()
    pen.penup()

    text_color = "white" if card['color'] != 'Yellow' else 'black'
    pen.color(text_color)
    pen.goto(x + 50, y + 65)
    pen.write(card['type'], align="center", font=("Arial", 30, "bold"))


# --- NEW: FUNCTION TO DRAW THE DECK PILE ---
def draw_deck_pile(x, y):
    """Draws the back of an UNO card to represent the deck."""
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.penup()
    pen.goto(x, y)
    pen.pendown()
    pen.color('black', '#222222')  # Dark grey fill for card back
    pen.begin_fill()
    for _ in range(2):
        pen.forward(100)
        pen.left(90)
        pen.forward(150)
        pen.left(90)
    pen.end_fill()
    pen.penup()

    # Draw the UNO logo
    pen.color('white')
    pen.goto(x + 50, y + 55)
    pen.write("UNO", align="center", font=("Arial", 28, "bold"))


# --- GAME MANAGER CLASS (No changes here) ---
class GameManager:
    """Manages the state and logic of an UNO game."""

    @staticmethod
    def create_uno_deck():
        """Creates and returns a standard deck of 108 UNO cards."""
        colors = ['Red', 'Yellow', 'Green', 'Blue']
        card_types = {
            '0': 1, '1': 2, '2': 2, '3': 2, '4': 2, '5': 2, '6': 2, '7': 2, '8': 2, '9': 2,
            'Skip': 2, 'Reverse': 2, 'Draw Two': 2
        }
        wild_cards = {'Wild': 4, 'Wild Draw Four': 4}
        deck = []
        for color in colors:
            for card_type, count in card_types.items():
                for _ in range(count):
                    deck.append({'color': color, 'type': card_type})
        for card_type, count in wild_cards.items():
            for _ in range(count):
                deck.append({'color': 'Wild', 'type': card_type})
        return deck


# --- MAIN GAME SETUP ---

# 1. Setup the screen
screen = turtle.Screen()
screen.setup(width=1000, height=600)
screen.bgcolor("darkgreen")
screen.title("UNO Game Setup")

# 2. Create and shuffle the deck using the GameManager
uno_deck = GameManager.create_uno_deck()
random.shuffle(uno_deck)
print(f"Deck created and shuffled with {len(uno_deck)} cards.")

# 3. Draw the deck pile on the left
draw_deck_pile(-350, 0)

# 4. Draw the first card for the discard pile
# Note: In a real game, you'd re-shuffle if this was a Wild Draw Four
discard_card = uno_deck.pop()
draw_uno_card(-200, 0, discard_card)

# 5. Deal and draw a starting hand of 7 cards
player_hand = []
for i in range(7):
    # Position each card so they overlap slightly
    card_x_position = -150 + (i * 40)
    card_y_position = -250

    # Draw a card from the top of the deck
    new_card = uno_deck.pop()
    player_hand.append(new_card)

    # Draw the card on the screen
    draw_uno_card(card_x_position, card_y_position, new_card)

print(f"Dealt 7 cards to the player. {len(uno_deck)} cards remain in the deck.")

# 6. Keep the window open
screen.exitonclick()