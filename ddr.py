import sys
import time
import random
import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluOrtho2D
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_HELVETICA_18

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
PLAYER_SPEED = 0.1
ARROW_SPEED = 0.01
MAX_ARROWS = 5
ARROW_GENERATION_DELAY = 1.0
ARROW_SIZE = 0.1  # Adjust arrow size for collision boundaries
arrows = []
player_position = 0.0
score = 0
missed_arrows = 0
game_over = False
last_arrow_generated_time = 0


def draw_arrow(direction, y):
    glBegin(GL_TRIANGLES)
    if direction == 'left':
        glColor3f(0.0, 1.0, 0.0)  # Green color for left arrow
        glVertex2f(-0.1, y + (ARROW_SIZE / 4))
        glVertex2f(-0.1, y - ARROW_SIZE)
        glVertex2f(-0.2, y - ARROW_SIZE / 2)
    elif direction == 'right':
        glColor3f(0.0, 0.0, 1.0)  # Blue color for right arrow
        glVertex2f(0.1, y - ARROW_SIZE / 2)
        glVertex2f(0.2, y + ARROW_SIZE / 4)
        glVertex2f(0.1, y + ARROW_SIZE)
    elif direction == 'up':
        glColor3f(1.0, 0.75, 0.8)  # Pink color for up arrow
        glVertex2f(0.0, y)
        glVertex2f(0.1, y)
        glVertex2f(0.05, y + ARROW_SIZE + 0.05) #-0.9 + ARROW_SIZE
    elif direction == 'down':
        glColor3f(1.0, 1.0, 0.0)  # Yellow color for down arrow
        glVertex2f(0.0, y + ARROW_SIZE + 0.05)
        glVertex2f(-0.1, y + ARROW_SIZE + 0.05)
        glVertex2f(-0.05, y)

    glEnd()


def draw_player():
    glBegin(GL_QUADS)
    glColor3f(1.0, 0.0, 0.0) # Red Box for invalid area
    glVertex2f(player_position - 0.2, -0.98)
    glVertex2f(player_position + 0.2, -0.98)
    glVertex2f(player_position + 0.2, -1.0)
    glVertex2f(player_position - 0.2, -1.0)
    glEnd()

def draw_hit_box():
    glColor3f(1.0, 1.0, 1.0) # white hit box line
    glBegin(GL_LINES)
    glVertex2f(player_position - 0.2, -0.87 + ARROW_SIZE)
    glVertex2f(player_position + 0.2, -0.87 + ARROW_SIZE)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(0.0, 1.0, 0.0)  # Green color for left arrow
    glVertex2f(player_position - 0.2, -0.9 + ARROW_SIZE / 4)
    glVertex2f(-0.1, -0.9 + ARROW_SIZE)
    glVertex2f(-0.1, -0.9 - ARROW_SIZE / 2)
    glEnd()
    
    glBegin(GL_LINE_LOOP)
    glColor3f(0.0, 0.0, 1.0)  # Blue color for right arrow
    glVertex2f(player_position + 0.2, -0.9 + ARROW_SIZE / 4)
    glVertex2f(0.1, -0.9 + ARROW_SIZE)
    glVertex2f(0.1, -0.9 - ARROW_SIZE / 2)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1.0, 0.75, 0.8)  # Pink color for up arrow
    glVertex2f(player_position + 0.05, -0.9 + ARROW_SIZE)
    glVertex2f(0.1, -0.9 - ARROW_SIZE / 2)
    glVertex2f(0.0, -0.9 - ARROW_SIZE / 2)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glColor3f(1.0, 1.0, 0.0)  # Yellow color for down arrow
    glVertex2f(player_position - 0.05, -0.9 - ARROW_SIZE / 2)
    glVertex2f(-0.1, -0.9 + ARROW_SIZE)
    glVertex2f(-0.0, -0.9 + ARROW_SIZE)
    glEnd()

def draw_text(text, x, y):
    glRasterPos2f(x, y)
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ctypes.c_int(ord(c)))

def draw_score():
    glColor3f(1.0, 1.0, 1.0) 
    draw_text(f"Score: {score}", -0.9, 0.9)

def draw_misses():
    glColor3f(1.0, 1.0, 1.0)
    draw_text(f"Misses: {missed_arrows}", -0.9, 0.8)

def draw_game_over():
    glColor3f(1.0, 1.0, 1.0) 
    draw_text(f"Game Over! Score: {score}. Press 'r' to reset", -0.9, 0.0)

def generate_arrow():
    global last_arrow_generated_time
    direction = random.choice(['left', 'right', 'up', 'down'])
    arrows.append({'direction': direction, 'y': 1.0})
    last_arrow_generated_time = time.time()

def key_callback(window, key, scancode, action, mods):
    global score, game_over

    hit_box_width = 0.4  # Adjust the hit box here

    if not game_over and action == glfw.PRESS:
        for arrow in arrows:
            arrow_x = arrow['direction'] == 'left' and -0.2 or 0.2

            if (
                arrow['y'] <= -0.9 + ARROW_SIZE
                and player_position - hit_box_width / 2 <= arrow_x <= player_position + hit_box_width / 2
            ):
                if key == glfw.KEY_LEFT and arrow['direction'] == 'left':
                    score += 1
                    arrows.remove(arrow)
                elif key == glfw.KEY_RIGHT and arrow['direction'] == 'right':
                    score += 1
                    arrows.remove(arrow)
                elif key == glfw.KEY_UP and arrow['direction'] == 'up':
                    score += 1
                    arrows.remove(arrow)
                elif key == glfw.KEY_DOWN and arrow['direction'] == 'down':
                    score += 1
                    arrows.remove(arrow)

        glfw.post_empty_event()

    elif game_over and action == glfw.PRESS and key == glfw.KEY_R:
        reset_game()
        score = 0
        glfw.post_empty_event()


def update():
    global arrows, missed_arrows, game_over

    if not game_over:
        current_time = time.time()
        for arrow in arrows:
            arrow['y'] -= ARROW_SPEED

        if current_time - last_arrow_generated_time > ARROW_GENERATION_DELAY:
            generate_arrow()

        if arrows and arrows[0]['y'] <= -1.0:
            missed_arrows += 1
            arrows.pop(0)

        if missed_arrows >= MAX_ARROWS:
            game_over = True
            print(f"Game Over! Score: {score}. Press 'r' to reset.")

        glfw.post_empty_event()

def display():
    glClear(GL_COLOR_BUFFER_BIT)

    draw_player()
    draw_score()
    draw_misses()
    draw_hit_box()

    if game_over:
        draw_game_over()
    else:
        for arrow in arrows:
            draw_arrow(arrow['direction'], arrow['y'])

    glfw.swap_buffers(window)

def reset_game():
    global arrows, player_position, score, missed_arrows, game_over
    arrows = []
    player_position = 0.0
    score = 0
    missed_arrows = 0
    game_over = False

def main():
    global window
    if not glfw.init():
        return

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Dance Dance Revolution", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glClearColor(0.0, 0.0, 0.0, 1.0)

    while not glfw.window_should_close(window):
        update()
        display()
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
