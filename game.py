import asyncio
import curses
import time
import random
import os

from curses_tools import draw_frame, read_controls
from physics import update_speed


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


def get_frame_size(text):
    """Calculate size of multiline text fragment. Returns pair (rows number, colums number)"""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


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

        await animate_spaceship(animation_frame_1)
        await run_spaceship(canvas, row, column)

        await animate_spaceship(animation_frame_2)
        await run_spaceship(canvas, row, column)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(canvas, garbage, speed=0.5):
    garbage_count = len(garbage)
    rows_number, columns_number = canvas.getmaxyx()

    while True:
        column = random.randint(1, columns_number)
        garbage_number = random.randint(0, garbage_count - 1)
        garbage_frame = garbage[garbage_number]

        column = max(column, 0)
        column = min(column, columns_number - 1)

        row = 0

        await sleep(GARBAGE_FALL_PAUSE)

        while row < rows_number:
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed


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

    gun_fire = [fire(canvas, start_row=max_row-ROW_INDENT_2, start_column=start_column,
                     rows_speed=ROWS_SPEED, columns_speed=COLUMNS_SPEED)]
    stars = [blink(canvas, row, column, symbol=random.choice(STAR_SYMBOLS)) for row, column in coordinates]

    spaceship = [drive_spaceship(canvas, start_row, start_column, rocket_1, rocket_2)]

    garbage_coroutine = [fill_orbit_with_garbage(canvas, garbage) for i in range(20)]

    COROUTINES = gun_fire + stars + spaceship + garbage_coroutine

    while len(COROUTINES) > 0:
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
