import turtle
import random
import typing


def create_dice_rolls(num_dice: int) -> typing.List[typing.Dict]:
    """Creates and returns a list of random dice rolls."""
    rolls = []
    for _ in range(num_dice):
        value = random.randint(1, 6)
        rolls.append({'value': value})
    return rolls


def draw_die(pen: turtle.Turtle, x: int, y: int, die: typing.Dict):
    """
    Draws a single game die at a specific location using a given turtle pen.
    - pen: The turtle object to use for drawing.
    - x, y: The bottom-left corner coordinates of the die.
    - die: A dictionary like {'value': 5}.
    """
    die_size = 80
    pip_radius = 8

    # --- Draw the main square of the die ---
    pen.penup()
    pen.goto(x, y)
    pen.pendown()
    pen.color('black', 'white')  # Black outline, white fill
    pen.begin_fill()
    for _ in range(4):
        pen.forward(die_size)
        pen.left(90)
    pen.end_fill()
    pen.penup()

    # --- Helper function to draw a single pip (dot) ---
    def draw_pip(pip_x, pip_y):
        pen.goto(pip_x, pip_y - pip_radius)  # Go to bottom of circle
        pen.pendown()
        pen.color('black', 'black')
        pen.begin_fill()
        pen.circle(pip_radius)
        pen.end_fill()
        pen.penup()

    # --- Calculate pip positions based on the die's value ---
    val = die.get('value')

    # Pre-calculate common coordinates based on die size
    col_1 = x + die_size * 0.25
    col_2 = x + die_size * 0.50
    col_3 = x + die_size * 0.75
    row_1 = y + die_size * 0.75
    row_2 = y + die_size * 0.50
    row_3 = y + die_size * 0.25

    # Use a more efficient structure to draw pips shared by multiple values
    if val in [1, 3, 5]:
        draw_pip(col_2, row_2)  # Center pip
    if val in [2, 3, 4, 5, 6]:
        draw_pip(col_1, row_1)  # Top-left
        draw_pip(col_3, row_3)  # Bottom-right
    if val in [4, 5, 6]:
        draw_pip(col_3, row_1)  # Top-right
        draw_pip(col_1, row_3)  # Bottom-left
    if val == 6:
        draw_pip(col_1, row_2)  # Middle-left
        draw_pip(col_3, row_2)  # Middle-right


if __name__ == "__main__":
    # --- Main Script (turtle demo) ---
    screen = turtle.Screen()
    screen.setup(width=900, height=600)
    screen.bgcolor("#1E5631")  # A nice dark green for a game table
    screen.title("Dice Game")
    screen.tracer(0)  # Turn off automatic screen updates for faster drawing

    main_pen = turtle.Turtle()
    main_pen.hideturtle()
    main_pen.speed(0)

    # Generate 10 random dice rolls
    dice_to_draw = create_dice_rolls(10)

    # --- Define layout for drawing the dice ---
    die_spacing = 100
    start_x = - (4.5 * die_spacing) / 2  # Center the rows
    start_y_top_row = 100
    start_y_bottom_row = -50

    print(f"Drawing {len(dice_to_draw)} dice...")

    for i, die_to_draw in enumerate(dice_to_draw):
        if i < 5:
            # First row
            die_x = start_x + (i * die_spacing)
            die_y = start_y_top_row
        else:
            # Second row
            die_x = start_x + ((i - 5) * die_spacing)
            die_y = start_y_bottom_row

        draw_die(main_pen, die_x, die_y, die_to_draw)

    screen.update()

    
    screen.exitonclick()