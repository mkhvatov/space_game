# 1) подключить ф-ю get_frame_size (curses_tools.py) к fill_orbit_with_garbage - ok

# 2) в fill_orbit_with_garbage в начале второго while сохранять в глобальгную переменную obstacles объект
# (корутина, которая сохраняет в глоб переменную)
# Obstacle (obstacle.row, obstacle.column, obstacle.rows_size, obstacle.columns_size, obstacle.uid)
# обновлять row и column у obstacle с уникальным uid каждую итерацию цикла

# 3) прикрепить корутину show_obstacles
