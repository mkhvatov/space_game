import asyncio
import curses
import time
import random
import os
import uuid

from curses_tools import draw_frame, read_controls, get_frame_size
from physics import update_speed
from obstacles import Obstacle, show_obstacles


ROCKET = './animation/rocket'
GARBAGE = './animation/garbage'

# list for all coroutines:
COROUTINES = []

MIN_TIME = 1

# constants for blink function:
BLINK_TIME_1 = 20
BLINK_TIME_2 = 3
BLINK_TIME_3 = 5
BLINK_TIME_4 = 3

# constants for fire function:
ROW_INDENT = 1
COLUMN_INDENT = 1
START_ROW = 0
START_COLUMN = 0

# constants for drive_spaceship function:
BORDER = 1

# constants for fill_orbit_with_garbage function:
GARBAGE_FALL_PAUSE = 80

# constants for main function:
MIDDLE_DIVISOR = 2
ROW_INDENT_2 = 2
COLUMN_INDENT_2 = 2
ROWS_SPEED = -1
COLUMNS_SPEED = 0
MIN_STARS_NUMBER = 35
MAX_STARS_NUMBER = 45
STARS_NUMBER = random.randint(MIN_STARS_NUMBER, MAX_STARS_NUMBER)
STAR_SYMBOLS = '+*.:'
LOOP_PAUSE = 0.1


def read_file(file_path):
    with open(file_path, "r") as file:
        file_content = file.read()
    return file_content


async def sleep(tics=1):
    for i in range(random.randint(MIN_TIME, tics)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(BLINK_TIME_1)

        canvas.addstr(row, column, symbol)
        await sleep(BLINK_TIME_2)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(BLINK_TIME_3)

        canvas.addstr(row, column, symbol)
        await sleep(BLINK_TIME_4)


async def fire(canvas, start_row, start_column, rows_speed, columns_speed):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - ROW_INDENT, columns - COLUMN_INDENT

    curses.beep()

    while START_ROW < row < max_row and START_COLUMN < column < max_column:
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return None

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(animation_frame):
    global spaceship_frame
    spaceship_frame = animation_frame


async def run_spaceship(canvas, row, column):
    draw_frame(canvas, row, column, spaceship_frame)
    await asyncio.sleep(0)
    draw_frame(canvas, row, column, spaceship_frame, negative=True)


async def save_fire_coordinates(row, column):
    global fire_coordinates
    fire_coordinates = (row, column)


async def delete_fire_coordinates():
    global fire_coordinates
    fire_coordinates = False


async def drive_spaceship(canvas, start_row, start_column, animation_frame_1, animation_frame_2):

    row, column = start_row, start_column
    row_speed = column_speed = 0

    rows_number, columns_number = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(animation_frame_1)

    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)

        row += row_speed
        upper_border = BORDER
        if row < upper_border:
            row = upper_border
        bottom_border = rows_number - frame_rows - BORDER
        if row > bottom_border:
            row = bottom_border

        column += column_speed
        left_border = BORDER
        if column < left_border:
            column = left_border
        right_border = columns_number - frame_columns - BORDER
        if column > right_border:
            column = right_border

        if space_pressed:
            spaceship_head_column = column + (frame_columns / 2)
            await save_fire_coordinates(row, spaceship_head_column)

        await animate_spaceship(animation_frame_1)
        await run_spaceship(canvas, row, column)

        await animate_spaceship(animation_frame_2)
        await run_spaceship(canvas, row, column)


async def fill_orbit_with_garbage(canvas, garbage, speed=0.5):
    garbage_count = len(garbage)
    rows_number, columns_number = canvas.getmaxyx()

    while True:
        column = random.randint(1, columns_number)
        garbage_number = random.randint(0, garbage_count - 1)
        garbage_frame = garbage[garbage_number]
        rows_size, columns_size = get_frame_size(garbage_frame)
        garbage_uid = uuid.uuid4()

        column = max(column, 0)
        column = min(column, columns_number - 1)

        row = 0

        await sleep(GARBAGE_FALL_PAUSE)

        try:
            while row < rows_number:

                obstacle_breaked = False
                for obstacle in obstacles_in_last_collisions:
                    if obstacle.uid == garbage_uid:
                        obstacle_breaked = True
                        break
                if obstacle_breaked:
                    break

                [obstacles.remove(obstacle) for obstacle in obstacles if obstacle.uid == garbage_uid]
                obstacle = Obstacle(row, column, rows_size, columns_size, garbage_uid)
                obstacles.append(obstacle)

                draw_frame(canvas, row, column, garbage_frame)
                await asyncio.sleep(0)
                draw_frame(canvas, row, column, garbage_frame, negative=True)
                row += speed
        finally:
            [obstacles.remove(obstacle) for obstacle in obstacles if obstacle.uid == garbage_uid]

            [obstacles_in_last_collisions.remove(obstacle) for obstacle in obstacles_in_last_collisions
             if obstacle.uid == garbage_uid]


def main(canvas):
    canvas.nodelay(True)

    rockets = [read_file(os.path.join(ROCKET, file_name)) for file_name in os.listdir(ROCKET)]
    rocket_1 = rockets[0]
    rocket_2 = rockets[1]

    garbage = [read_file(os.path.join(GARBAGE, file_name)) for file_name in os.listdir(GARBAGE)]

    canvas.border()
    curses.curs_set(False)

    max_row, max_column = canvas.getmaxyx()
    start_row, start_column = round(max_row/MIDDLE_DIVISOR), round(max_column/MIDDLE_DIVISOR)

    coordinates = [(random.randint(ROW_INDENT_2, max_row-ROW_INDENT_2),
                    random.randint(COLUMN_INDENT_2, max_column-COLUMN_INDENT_2)) for i in range(STARS_NUMBER)]

    stars = [blink(canvas, row, column, symbol=random.choice(STAR_SYMBOLS)) for row, column in coordinates]

    spaceship = [drive_spaceship(canvas, start_row, start_column, rocket_1, rocket_2)]

    garbage_coroutine = [fill_orbit_with_garbage(canvas, garbage) for i in range(20)]

    COROUTINES = stars + spaceship + garbage_coroutine

    global fire_coordinates
    fire_coordinates = False

    global obstacles
    obstacles = []

    global obstacles_in_last_collisions
    obstacles_in_last_collisions = []

    obstacles_coroutine = show_obstacles(canvas, obstacles)
    COROUTINES.append(obstacles_coroutine)

    while len(COROUTINES) > 0:
        if fire_coordinates:
            row, column = fire_coordinates
            COROUTINES.append(fire(canvas, start_row=row, start_column=column,
                                   rows_speed=ROWS_SPEED, columns_speed=COLUMNS_SPEED))
            COROUTINES.append(delete_fire_coordinates())
        try:
            for coroutine in COROUTINES:
                coroutine.send(None)
            canvas.refresh()
            time.sleep(LOOP_PAUSE)
        except StopIteration:
            COROUTINES.remove(coroutine)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
