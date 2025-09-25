import turtle
CARD_WIDTH = 50
CARD_HEIGHT = 70
screen = turtle.Screen()
screen.bgcolor("Green")
for _ in range(100):
    turtle.forward(300)
    turtle.left(260)

def draw_card_front(t, x, y, card):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.color("white", "white")
    t.begin_fill()
    t.setheading(0)
    for _ in range(2):
        t.forward(CARD_WIDTH)
        t.right(90)
        t.forward(CARD_HEIGHT)
        t.right(90)
    t.end_fill()