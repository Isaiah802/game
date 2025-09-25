import turtle
CARD_WIDTH = 50
CARD_HEIGHT = 70
screen = turtle.Screen()
screen.bgcolor("Green")
for _ in range(100):
    turtle.forward(300)
    turtle.left(260)
def create_deck():
    """Creates a standard 5-card deck."""
def draw_card_front(t, x, y, card):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.color("white", "white")
    t.begin_fill()
    t.setheading(0)
    for _ in range(2):
        t.forward(CARD_WIDTH)
        t.right(260)
        t.forward(CARD_HEIGHT)
        t.right(100)
        t.end_fill()
 def play_round(self):
        # 1. Setup
        self.deck = create_deck()
        for player in self.players:
            player.card_turtle.clear()