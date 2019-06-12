from physics import update_speed


# корабль стоит на месте
row = column = 10
row_speed = column_speed = 0

# теперь рванул вверх
row_speed, column_speed = update_speed(row_speed, column_speed, -1, 0)


if __name__ == '__main__':
    a = 0
    while a < 10:
        row_speed, column_speed = update_speed(row_speed, column_speed, -1, 0)
        row += row_speed
        column += column_speed
        print(row, column)
        a += 1
