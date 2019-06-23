# constants for draw_frame function:
START_ROW_FRAME = 0
START_COLUMN_FRAME = 0
ROW_INDENT_1 = 1
COLUMN_INDENT_1 = 1

# constants for read_controls function:
START_DIRECTION = 0
NO_INPUT = -1

UP_STEP = -1
DOWN_STEP = 1
LEFT_STEP = -1
RIGHT_STEP = 1

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


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
