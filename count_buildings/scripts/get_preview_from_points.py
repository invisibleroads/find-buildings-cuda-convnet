import numpy as np
import sys
from crosscompute.libraries import script
from functools import partial
from geometryIO import load_points
from os.path import join
from random import sample
from skimage.draw import circle, circle_perimeter

from ..libraries.satellite_image import (
    SatelliteImage, get_pixel_frame_from_pixel_center, enhance_array,
    render_enhanced_array)


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='satellite image')
        starter.add_argument(
            '--points_path', metavar='PATH', required=True,
            help='building locations')
        starter.add_argument(
            '--tile_metric_dimensions', metavar='WIDTH,HEIGHT',
            type=script.parse_dimensions, default=(1000, 1000),
            help='dimensions of extracted tile in metric units')


def run(target_folder, image_path, points_path, tile_metric_dimensions):
    image = SatelliteImage(image_path)
    projected_xys = load_points(points_path, targetProj4=image.proj4)[1]
    pixel_xys = [image.to_pixel_xy(_) for _ in projected_xys]

    image_pixel_frame = (0, 0), image.pixel_dimensions
    image_pixel_xys = filter(get_in_frame(image_pixel_frame), pixel_xys)

    selected_pixel_frame = get_pixel_frame(image.to_pixel_dimensions(
        tile_metric_dimensions), image_pixel_xys, image,
        random_iteration_count=10)
    selected_pixel_xys = filter(
        get_in_frame(selected_pixel_frame), image_pixel_xys)

    pixel_x, pixel_y = selected_pixel_frame[0]
    relate = lambda (x, y): (x - pixel_x, y - pixel_y)
    relative_pixel_xys = [relate(_) for _ in selected_pixel_xys]

    array = image.get_array_from_pixel_frame(selected_pixel_frame)
    enhanced_array = enhance_array(array)
    painted_array = paint_spots(enhanced_array, relative_pixel_xys)

    target_path = join(target_folder, 'pul%dx%d.jpg' % (pixel_x, pixel_y))
    render_enhanced_array(target_path, painted_array)
    return {
        'selected_pixel_upper_left': selected_pixel_frame[0],
        'selected_pixel_dimensions': selected_pixel_frame[1],
        'selected_point_count': len(relative_pixel_xys),
    }


def get_in_frame(pixel_frame):
    (x1, y1), (pixel_width, pixel_height) = pixel_frame
    x2, y2 = x1 + pixel_width, y1 + pixel_height
    return lambda (x, y): (x1 <= x) and (x <= x2) and (y1 <= y) and (y <= y2)


def get_pixel_frame(
        target_pixel_dimensions, source_pixel_xys, source_image,
        random_iteration_count):
    # Fit pixel_dimensions to source_image.pixel_dimensions
    target_pixel_width, target_pixel_height = target_pixel_dimensions
    source_pixel_width, source_pixel_height = source_image.pixel_dimensions
    pixel_width = min(target_pixel_width, source_pixel_width)
    pixel_height = min(target_pixel_height, source_pixel_height)
    pixel_dimensions = pixel_width, pixel_height
    # Get pixel_frames
    pixel_xys = sample(source_pixel_xys, random_iteration_count)
    pixel_frames = get_pixel_frames(pixel_xys, pixel_dimensions, source_image)
    # Pick the pixel_frame with the most number of source_pixel_xys
    rank_pixel_frame = partial(count_pixel_xys_in_frame, source_pixel_xys)
    return max(pixel_frames, key=rank_pixel_frame)


def paint_spots(target_array, pixel_xys):
    target_array = np.copy(target_array)
    yellow = target_array[:, :, 0].max(), target_array[:, :, 1].max(), 0
    black = 0, 0, 0
    for pixel_x, pixel_y in pixel_xys:
        rows, columns = circle(pixel_y, pixel_x, 3)
        target_array[rows, columns] = yellow
        rows, columns = circle_perimeter(pixel_y, pixel_x, 3, method='andres')
        target_array[rows, columns] = black
    return target_array


def get_pixel_frames(pixel_xys, pixel_dimensions, source_image):
    rough_pixel_frames = (get_pixel_frame_from_pixel_center(
        _, pixel_dimensions) for _ in pixel_xys)
    image_pixel_width, image_pixel_height = source_image.pixel_dimensions
    final_pixel_frames = []
    for (pixel_x, pixel_y), (pixel_width, pixel_height) in rough_pixel_frames:
        pixel_x = adjust_placement(pixel_x, pixel_width, image_pixel_width)
        pixel_y = adjust_placement(pixel_y, pixel_height, image_pixel_height)
        final_pixel_frames.append(
            ((pixel_x, pixel_y), (pixel_width, pixel_height)))
    return final_pixel_frames


def count_pixel_xys_in_frame(pixel_xys, pixel_frame):
    in_frame = get_in_frame(pixel_frame)
    return sum(in_frame(_) for _ in pixel_xys)


def adjust_placement(t, length, maximum_length):
    if t < 0:
        return 0
    if t + length > maximum_length:
        return maximum_length - length
    return t
