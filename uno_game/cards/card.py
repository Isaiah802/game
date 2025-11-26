import os
import sys
import os
# Ensure uno_game directory itself is in sys.path for imports
uno_game_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if uno_game_dir not in sys.path:
    sys.path.insert(0, uno_game_dir)
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel, DirectScrolledList
from items import registry, Inventory
import random
import math

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3, Point3, LColor, Plane,
    BitMask32, CardMaker, NodePath, 
    Texture, PNMImage, TransparencyAttrib,
    DirectionalLight, AmbientLight,
    Material, AntialiasAttrib, TextNode,
    Filename, loadPrcFileData, LineSegs
)
from panda3d.bullet import (
    BulletWorld, BulletPlaneShape, 
    BulletRigidBodyNode, BulletBoxShape, 
    BulletDebugNode
)
from direct.gui.OnscreenText import OnscreenText

# --- CONFIGURATION ---
loadPrcFileData('', 'load-file-type p3gltf')

# --- 1. PHYSICS BOX DIMENSIONS (The Invisible Container) ---
# Adjust these until the "Green Wireframe" box matches your table's play area
TABLE_WIDTH_PHYSICS = 18.0   
TABLE_DEPTH_PHYSICS = 12.0   
WALL_HEIGHT = 15.0

# --- 2. VISUAL TABLE ALIGNMENT (The 3D Model) ---
# Use F1 to see the mismatch, then change these numbers.
TABLE_MODEL_SCALE = 12     # Make the table bigger/smaller
TABLE_VISUAL_Z = -6   # Move table UP (+) or DOWN (-) to match floor

# --- DICE CONFIG ---
DIE_SIZE = 0.8          
FRICTION_FELT = 0.9     
BOUNCINESS = 0.5        
DAMPING_ANGULAR = 0.5   

# --- ASSETS ---
FOLDER_NAME = "dice"
DICE_FILE_NAME = "test3.glb" 
TABLE_FILE_NAME = "poker-table.glb" 
DICE_MODEL_SCALE = 10.0 

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- SCORING CALIBRATION ---
DIE_AXIS_MAPPING = { "UP": 4, "DOWN": 3, "RIGHT": 2, "LEFT": 1, "FWD": 5, "BACK": 6 }
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
    screen.bgcolor("#1C522E")  # A nice dark green for a game table
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