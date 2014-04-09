import math


def get_cover(a, b, interval):
    a_cover = int(math.ceil(-1 + a / float(interval)) * interval)
    b_cover = int(math.floor(+1 + b / float(interval)) * interval)
    return xrange(a_cover, b_cover, interval)


def get_tile_index(pixel_upper_left, interval_dimensions, row_count):
    pixel_x, pixel_y = pixel_upper_left
    interval_x, interval_y = interval_dimensions
    return row_count * pixel_x / interval_x + pixel_y / interval_y


values = get_cover(25, 45, 10)
assert list(values) == [20, 30, 40]

values = get_cover(10, 40, 10)
assert list(values) == [0, 10, 20, 30, 40]

tile_index = get_tile_index(
    pixel_upper_left=(10, 10),
    interval_dimensions=(10, 10),
    row_count=3)
assert tile_index == 4


def get_row_count(height, interval_y):
    return int(math.ceil(height / float(interval_y)))


xs = xrange(0, 65, 10)
ys = xrange(0, 60, 10)
row_count = get_row_count(60, 10)
assert len(ys) == row_count
from itertools import product
packs = [(get_tile_index(_, (10, 10), row_count), _) for _ in product(xs, ys)]
assert packs == list(enumerate(product(xs, ys)))
