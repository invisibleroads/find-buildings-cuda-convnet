import numpy as np
import rtree.index
import sys
from crosscompute.libraries import script
from functools import partial
from geometryIO import load_points
from os.path import basename, join
from random import sample
from scipy.stats import entropy
from skimage.draw import circle, circle_perimeter

from ..libraries.satellite_image import (
    SatelliteImage, PixelScope, get_pixel_frame_from_pixel_center,
    enhance_array, render_enhanced_array, render_array)


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='satellite image')
        starter.add_argument(
            '--points_path', metavar='PATH',
            help='building locations')
        starter.add_argument(
            '--tile_pixel_dimensions', metavar='WIDTH,HEIGHT',
            type=script.parse_integer_dimensions, default=(500, 500),
            help='dimensions of extracted tile in pixels')
        starter.add_argument(
            '--random_iteration_count', metavar='INTEGER',
            type=int, default=25,
            help='')


def run(
        target_folder, image_path, points_path, tile_pixel_dimensions,
        random_iteration_count):
    image = SatelliteImage(image_path)
    if points_path:
        projected_xys = load_points(points_path, targetProj4=image.proj4)[1]
        pixel_xys = [image.to_pixel_xy(_) for _ in projected_xys]
    else:
        pixel_xys = []

    if pixel_xys:
        image_pixel_frame = (0, 0), image.pixel_dimensions
        image_pixel_xys = filter(get_in_frame(image_pixel_frame), pixel_xys)

        selected_pixel_frame = get_pixel_frame(
            tile_pixel_dimensions, image_pixel_xys, image,
            random_iteration_count)
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
    else:
        image_pixel_dimensions = image.pixel_dimensions

        image_pixel_width, image_pixel_height = image_pixel_dimensions
        preview_pixel_width, preview_pixel_height = tile_pixel_dimensions
        preview_pixel_width = min(preview_pixel_width, image_pixel_width)
        preview_pixel_height = min(preview_pixel_height, image_pixel_height)
        preview_pixel_dimensions = preview_pixel_width, preview_pixel_height

        pixel_scope = PixelScope(image, preview_pixel_dimensions)
        random_iteration_count = 10
        pixel_centers = [
            pixel_scope.get_random_pixel_center() for x in xrange(
                random_iteration_count)]
        pixel_frames = [
            pixel_scope.get_pixel_frame_from_pixel_center(
                x) for x in pixel_centers]
        selected_pixel_frames = select_unique_pixel_frames(pixel_frames)

        preview_image_names = []

        packs = [(
            pixel_frame,
            pixel_scope.get_array_from_pixel_frame(pixel_frame)
        ) for pixel_frame in selected_pixel_frames]
        ranked_packs = sorted(
            packs, key=lambda x: -entropy(np.histogram(x[1])[0]))

        maximum_preview_count = 1
        selected_packs = ranked_packs[:maximum_preview_count]
        for selected_index, (
            selected_pixel_frame, selected_array,
        ) in enumerate(selected_packs):
            pixel_x, pixel_y = selected_pixel_frame[0]
            preview_image_path = join(
                target_folder, 'pul%dx%d.jpg' % (pixel_x, pixel_y))
            preview_image_names.append(basename(preview_image_path))
            render_array(preview_image_path, selected_array)
        return {
            'selected_pixel_upper_left': selected_pixel_frame[0],
            'selected_pixel_dimensions': selected_pixel_frame[1],
            'selected_point_count': 0,
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
    if len(source_pixel_xys) > random_iteration_count:
        pixel_xys = sample(source_pixel_xys, random_iteration_count)
    else:
        pixel_xys = source_pixel_xys
    pixel_frames = get_pixel_frames(pixel_xys, pixel_dimensions, source_image)
    # Pick the pixel_frame with the most number of source_pixel_xys
    rank_pixel_frame = partial(count_pixel_xys_in_frame, source_pixel_xys)
    return max(pixel_frames, key=rank_pixel_frame)


def paint_spots(target_array, pixel_xys):
    target_array = np.copy(target_array)
    yellow = target_array[:, :, 0].max(), target_array[:, :, 1].max(), 0
    black = 0, 0, 0
    for pixel_x, pixel_y in pixel_xys:
        paint_array(target_array, circle(
            pixel_y, pixel_x, 3), yellow)
        paint_array(target_array, circle_perimeter(
            pixel_y, pixel_x, 3, method='andres'), black)
    return target_array


def paint_array(target_array, (rows, columns), color):
    try:
        target_array[rows, columns] = color
    except IndexError:
        row_count, column_count = target_array.shape[:2]
        indices = (
            rows >= 0) & (rows < row_count) & (
            columns >= 0) & (columns < column_count)
        target_array[rows[indices], columns[indices]] = color


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


def select_unique_pixel_frames(pixel_frames):
    selected_pixel_frames = []
    pixel_frame_tree = rtree.index.Index()
    for pixel_frame in pixel_frames:
        (pixel_x, pixel_y), (pixel_width, pixel_height) = pixel_frame
        x1, y1 = pixel_x, pixel_y
        x2, y2 = pixel_x + pixel_width, pixel_y + pixel_height
        pixel_box = x1, y1, x2, y2
        if not pixel_frame_tree.count(pixel_box):
            pixel_frame_tree.insert(0, pixel_box)
            selected_pixel_frames.append(pixel_frame)
    return selected_pixel_frames
