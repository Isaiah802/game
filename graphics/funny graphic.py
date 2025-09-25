import turtle
CARD_WIDTH = 50
CARD_HEIGHT = 70
screen = turtle.Screen()
screen.bgcolor("Green")
def draw_card():
    card = turtle.Turtle()
    card.shape("square")
    card.color("red")
    card.penup()
    card.goto(-CARD_WIDTH/2, -CARD_HEIGHT/2)
    card.pendown()
    card.begin_fill()
    card.goto(-CARD_WIDTH/2, -CARD_HEIGHT/2)

