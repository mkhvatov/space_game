import asyncio
import curses
import time
import random
import os


ANIMATION_FOLDER = './animation'

# constants for blink function:
MIN_BLINK_TIME = 1
BLINK_TIME_1 = 20
BLINK_TIME_2 = 3
BLINK_TIME_3 = 5
BLINK_TIME_4 = 3

# constants for fire function:
ROW_INDENT = 1
COLUMN_INDENT = 1
START_ROW = 0
START_COLUMN = 0

# constants for draw_frame function:
START_ROW_FRAME = 0
START_COLUMN_FRAME = 0
ROW_INDENT_1 = 1
COLUMN_INDENT_1 = 1

# constants for animate_spaceship function:
BORDER = 1

# constants for read_controls function:
START_DIRECTION = 0
NO_INPUT = -1
UP_STEP = -5
DOWN_STEP = 5
LEFT_STEP = -5
RIGHT_STEP = 5
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

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


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(random.randint(MIN_BLINK_TIME, BLINK_TIME_1)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(random.randint(MIN_BLINK_TIME, BLINK_TIME_2)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(random.randint(MIN_BLINK_TIME, BLINK_TIME_3)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(random.randint(MIN_BLINK_TIME, BLINK_TIME_4)):
            await asyncio.sleep(0)


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


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas. Erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < START_ROW_FRAME:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < START_COLUMN_FRAME:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - ROW_INDENT_1 and column == columns_number - COLUMN_INDENT_1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def animate_spaceship(canvas, start_row, start_column, animation_frame_1, animation_frame_2):

    row, column = start_row, start_column
    rows_number, columns_number = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(animation_frame_1)

    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        row += rows_direction
        upper_border = BORDER
        if row < upper_border:
            row = upper_border
        bottom_border = rows_number - frame_rows - BORDER
        if row > bottom_border:
            row = bottom_border

        column += columns_direction
        left_border = BORDER
        if column < left_border:
            column = left_border
        right_border = columns_number - frame_columns - BORDER
        if column > right_border:
            column = right_border

        draw_frame(canvas, row, column, animation_frame_1)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, animation_frame_1, negative=True)

        draw_frame(canvas, row, column, animation_frame_2)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, animation_frame_2, negative=True)


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = START_DIRECTION
    space_pressed = False

    while True:

        pressed_key_code = canvas.getch()

        if pressed_key_code == NO_INPUT:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = UP_STEP

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = DOWN_STEP

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = RIGHT_STEP

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = LEFT_STEP

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def get_frame_size(text):
    """Calculate size of multiline text fragment. Returns pair (rows number, colums number)"""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def main(canvas):
    canvas.nodelay(True)

    rockets = [read_file(os.path.join(ANIMATION_FOLDER, file_name)) for file_name in os.listdir(ANIMATION_FOLDER)]
    rocket_1 = rockets[0]
    rocket_2 = rockets[1]

    canvas.border()
    curses.curs_set(False)

    max_row, max_column = canvas.getmaxyx()
    start_row, start_column = round(max_row/MIDDLE_DIVISOR), round(max_column/MIDDLE_DIVISOR)

    coordinates = [(random.randint(ROW_INDENT_2, max_row-ROW_INDENT_2),
                    random.randint(COLUMN_INDENT_2, max_column-COLUMN_INDENT_2)) for i in range(STARS_NUMBER)]

    gun_fire = [fire(canvas, start_row=max_row-ROW_INDENT_2, start_column=start_column,
                     rows_speed=ROWS_SPEED, columns_speed=COLUMNS_SPEED)]
    stars = [blink(canvas, row, column, symbol=random.choice(STAR_SYMBOLS)) for row, column in coordinates]

    spaceship = [animate_spaceship(canvas, start_row, start_column, rocket_1, rocket_2)]

    coroutines = gun_fire + stars + spaceship

    while len(coroutines) > 0:
        try:
            for coroutine in coroutines:
                coroutine.send(None)
            canvas.refresh()
            time.sleep(LOOP_PAUSE)
        except StopIteration:
            coroutines.remove(coroutine)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
