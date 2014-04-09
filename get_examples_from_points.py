import h5py
import operator
import os
from geometryIO import get_transformPoint
from geometryIO import load_points
from scipy.sparse import lil_matrix

from count_buildings.libraries import calculator
from count_buildings.libraries import disk
from count_buildings.libraries import satellite_image
from count_buildings.libraries import script
from count_buildings.libraries.tree import RTree


def run(
        target_folder, image_path, point_path,
        example_dimensions, positive_count, negative_count, save_images):
    image_scope = satellite_image.ImageScope(image_path, example_dimensions)
    example_pixel_dimensions = image_scope.scope_pixel_dimensions
    point_proj4, positive_centers = load_points(point_path)[:2]
    transform_point = get_transformPoint(point_proj4, image_scope.proj4)
    positive_pixel_centers = [
        image_scope.to_pixel_xy(transform_point(*_)) for _ in positive_centers]
    example_h5 = get_example_h5(target_folder, example_dimensions)

    if positive_count is None:
        positive_count = len(positive_pixel_centers)
    if negative_count is None:
        negative_count = estimate_negative_count(
            image_scope, positive_pixel_centers)

    save_positive_examples(
        example_h5, target_folder, example_pixel_dimensions,
        image_scope, positive_pixel_centers, positive_count, save_images)
    save_negative_examples(
        example_h5, target_folder, example_pixel_dimensions,
        image_scope, positive_pixel_centers, negative_count, save_images)
    return dict(
        example_pixel_dimensions=example_pixel_dimensions,
        positive_count=positive_count,
        negative_count=negative_count)


def get_example_h5(target_folder, example_dimensions):
    example_name = 'e%dx%d' % tuple(example_dimensions)
    example_path = os.path.join(target_folder, example_name + '.h5')
    return h5py.File(example_path, 'w')


def save_image(image_scope, target_folder, pixel_center, array):
    example_path = get_example_path(target_folder, pixel_center)
    image_scope.save_image(example_path, array[:, :, :3])


def get_example_path(target_folder, pixel_center):
    example_name = 'pce%dx%d.jpg' % tuple(pixel_center)
    return os.path.join(target_folder, example_name)


def estimate_negative_count(image_scope, positive_pixel_centers):
    canvas = lil_matrix(image_scope.pixel_dimensions, dtype='bool')
    # Compute the positive pixel area
    for positive_pixel_center in positive_pixel_centers:
        pixel_frame = image_scope.get_pixel_frame_from_pixel_center(
            positive_pixel_center)
        (pixel_x, pixel_y), (pixel_width, pixel_height) = pixel_frame
        canvas[
            pixel_x:pixel_x + pixel_width,
            pixel_y:pixel_y + pixel_height] = 1
    positive_pixel_area = canvas.sum()
    # Compute the negative pixel area
    image_pixel_area = reduce(operator.mul, image_scope.pixel_dimensions)
    negative_pixel_area = image_pixel_area - positive_pixel_area
    # Compute the ratio of negatives to positives
    negative_area_over_positive_area = negative_pixel_area / float(
        positive_pixel_area)
    # Estimate the required number of negative examples
    positive_count = len(positive_pixel_centers)
    return calculator.round_integer(
        negative_area_over_positive_area * positive_count)


def save_positive_examples(
        example_h5, target_folder, (example_pixel_width, example_pixel_height),
        image_scope, positive_pixel_centers, positive_count, save_images):
    if save_images:
        positives_folder = disk.replace_folder(target_folder, 'positives')
    positive_arrays = example_h5.create_dataset(
        'positive/arrays', shape=(
            positive_count, example_pixel_height, example_pixel_width,
            image_scope.band_count), dtype=image_scope.array_dtype)
    for positive_index in xrange(positive_count):
        pixel_center = positive_pixel_centers[positive_index]
        # Get array
        array = image_scope.get_array_from_pixel_center(pixel_center)
        positive_arrays[positive_index, :, :, :] = array
        if save_images:
            save_image(image_scope, positives_folder, pixel_center, array)
    example_h5.create_dataset(
        'positive/pixel_centers',
        data=positive_pixel_centers, dtype=image_scope.pixel_dtype)
    return positive_pixel_centers


def save_negative_examples(
        example_h5, target_folder, (example_pixel_width, example_pixel_height),
        image_scope, positive_pixel_centers, negative_count, save_images):
    if save_images:
        negatives_folder = disk.replace_folder(target_folder, 'negatives')
    negative_pixel_centers = []
    negative_arrays = example_h5.create_dataset(
        'negative/arrays', shape=(
            negative_count, example_pixel_height, example_pixel_width,
            image_scope.band_count), dtype=image_scope.array_dtype)
    negative_pixel_center_iter = yield_negative_pixel_center(
        image_scope, positive_pixel_centers)
    for negative_index in xrange(negative_count):
        pixel_center = negative_pixel_center_iter.next()
        negative_pixel_centers.append(pixel_center)
        # Get array
        array = image_scope.get_array_from_pixel_center(pixel_center)
        negative_arrays[negative_index, :, :, :] = array
        if save_images:
            save_image(image_scope, negatives_folder, pixel_center, array)
    example_h5.create_dataset(
        'negative/pixel_centers',
        data=negative_pixel_centers, dtype=image_scope.pixel_dtype)
    return negative_pixel_centers


def yield_negative_pixel_center(image_scope, positive_pixel_centers):
    point_rtree = RTree(positive_pixel_centers)
    while True:
        pixel_center = image_scope.get_random_pixel_center()
        # Retry if the pixel_frame contains a positive_pixel_center
        pixel_bounds = image_scope.get_pixel_bounds_from_pixel_center(
            pixel_center)
        if point_rtree.intersects(pixel_bounds):
            continue
        yield pixel_center


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        '--image_path', metavar='PATH', required=True,
        help='satellite image')
    argument_parser.add_argument(
        '--point_path', metavar='PATH', required=True,
        help='building locations')
    argument_parser.add_argument(
        '--example_dimensions', metavar='WIDTH,HEIGHT', required=True,
        type=script.parse_dimensions,
        help='dimensions of extracted example in geographic units')
    argument_parser.add_argument(
        '--positive_count', metavar='INTEGER',
        type=int,
        help='maximum number of positive examples to extract')
    argument_parser.add_argument(
        '--negative_count', metavar='INTEGER',
        type=int,
        help='maximum number of negative examples to extract')
    argument_parser.add_argument(
        '--save_images', action='store_true',
        help='save images of positive and negative examples')
    arguments = script.parse_arguments(argument_parser)
    variables = run(**arguments.__dict__)
    script.save_run(arguments, variables, verbose=True)
