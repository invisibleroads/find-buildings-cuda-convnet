import h5py
import numpy as np
import operator
import sys
from crosscompute.libraries import script
from geometryIO import get_transformPoint, load_points
from os.path import join

from ..libraries import calculator
from ..libraries import disk
from ..libraries import satellite_image
from ..libraries.tree import RTree


EXAMPLES_NAME = 'examples.h5'


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='satellite image')
        starter.add_argument(
            '--positive_points_paths', metavar='PATH', required=True,
            nargs='+',
            help='positive locations')
        starter.add_argument(
            '--negative_points_paths', metavar='PATH',
            nargs='+',
            help='negative locations')
        starter.add_argument(
            '--example_metric_dimensions', metavar='WIDTH,HEIGHT',
            type=script.parse_dimensions, required=True,
            help='dimensions of extracted example in metric units')
        starter.add_argument(
            '--maximum_positive_count', metavar='INTEGER',
            type=script.parse_size,
            help='maximum number of positive examples to extract')
        starter.add_argument(
            '--maximum_negative_count', metavar='INTEGER',
            type=script.parse_size,
            help='maximum number of negative examples to extract')
        starter.add_argument(
            '--save_images', action='store_true',
            help='save images of positive and negative examples')


def run(
        target_folder, image_path,
        positive_points_paths, negative_points_paths,
        example_metric_dimensions,
        maximum_positive_count, maximum_negative_count, save_images):
    examples_h5 = get_examples_h5(target_folder)
    image_scope = satellite_image.ImageScope(
        image_path, example_metric_dimensions)
    positive_pixel_centers = get_pixel_centers(
        positive_points_paths, image_scope)
    negative_pixel_centers = get_pixel_centers(
        negative_points_paths, image_scope)

    positive_count = trim_to_minimum(
        len(positive_pixel_centers),
        maximum_positive_count)
    negative_count = trim_to_minimum(
        estimate_negative_count(image_scope, positive_pixel_centers),
        maximum_negative_count)
    example_count = positive_count + negative_count
    print 'positive_fraction = %s' % (positive_count / float(example_count))

    save_positive_examples(
        save_images and disk.replace_folder(target_folder, 'positives'),
        image_scope, positive_pixel_centers, positive_count, examples_h5)
    save_negative_examples(
        save_images and disk.replace_folder(target_folder, 'negatives'),
        image_scope, negative_pixel_centers, negative_count, examples_h5,
        positive_pixel_centers)
    return dict(
        example_pixel_dimensions=image_scope.scope_pixel_dimensions,
        positive_fraction=positive_count / float(example_count),
        positive_count=positive_count,
        negative_count=negative_count)


def get_examples_h5(target_folder):
    return h5py.File(join(target_folder, EXAMPLES_NAME), 'w')


def get_pixel_centers(points_paths, image_scope):
    if not points_paths:
        return []
    pixel_centers = []
    for points_path in points_paths:
        points_proj4, projected_centers = load_points(points_path)[:2]
        transform_point = get_transformPoint(points_proj4, image_scope.proj4)
        pixel_centers.extend(filter(image_scope.is_pixel_center, (
            image_scope.to_pixel_xy(transform_point(
                *_)) for _ in projected_centers)))
    return pixel_centers


def trim_to_minimum(actual_maximum, desired_maximum):
    return min(actual_maximum, desired_maximum or actual_maximum)


def estimate_negative_count(image_scope, positive_pixel_centers):
    canvas = np.zeros(tuple(image_scope.pixel_dimensions), dtype='bool')
    # Compute the positive pixel area
    for index, positive_pixel_center in enumerate(positive_pixel_centers):
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
    return calculator.round_number(
        negative_area_over_positive_area * positive_count)


def save_positive_examples(
        target_folder, image_scope, positive_pixel_centers,
        positive_count, examples_h5):
    pixel_width, pixel_height = image_scope.scope_pixel_dimensions
    positive_arrays = examples_h5.create_dataset(
        'positive/arrays', shape=(
            positive_count, pixel_height, pixel_width,
            image_scope.band_count), dtype=image_scope.array_dtype)
    positive_index = 0
    for positive_index in xrange(positive_count):
        if positive_index % 1000 == 0:
            print '%s / %s' % (positive_index, positive_count - 1)
        pixel_center = positive_pixel_centers[positive_index]
        array = save_example_array(target_folder, image_scope, pixel_center)
        positive_arrays[positive_index, :, :, :] = array
    save_pixel_centers(
        examples_h5, 'positive', positive_pixel_centers[:positive_count],
        image_scope)
    print '%s / %s' % (positive_index, positive_count - 1)


def save_negative_examples(
        target_folder, image_scope, negative_pixel_centers,
        negative_count, examples_h5, positive_pixel_centers):
    pixel_width, pixel_height = image_scope.scope_pixel_dimensions
    negative_arrays = examples_h5.create_dataset(
        'negative/arrays', shape=(
            negative_count, pixel_height, pixel_width,
            image_scope.band_count), dtype=image_scope.array_dtype)
    pixel_centers = []
    negative_pixel_center_iter = yield_negative_pixel_center(
        image_scope, negative_pixel_centers, positive_pixel_centers)
    for negative_index in xrange(negative_count):
        if negative_index % 1000 == 0:
            print '%s / %s' % (negative_index, negative_count - 1)
        pixel_center = negative_pixel_center_iter.next()
        array = save_example_array(target_folder, image_scope, pixel_center)
        negative_arrays[negative_index, :, :, :] = array
        pixel_centers.append(pixel_center)
    save_pixel_centers(
        examples_h5, 'negative', pixel_centers[:negative_count],
        image_scope)
    print '%s / %s' % (negative_index, negative_count - 1)


def save_example_array(target_folder, image_scope, pixel_center):
    array = image_scope.get_array_from_pixel_center(pixel_center)
    try:
        image_scope.save_image(
            join(target_folder, 'pce%dx%d.jpg' % tuple(pixel_center)), array)
    except AttributeError:
        pass
    return array


def save_pixel_centers(examples_h5, category, pixel_centers, image_scope):
    pixel_centers = examples_h5.create_dataset(
        '%s/pixel_centers' % category,
        data=pixel_centers, dtype=image_scope.pixel_coordinate_dtype)
    pixel_centers.attrs['calibration_pack'] = image_scope.calibration_pack
    pixel_centers.attrs['proj4'] = image_scope.proj4


def yield_negative_pixel_center(
        image_scope, negative_pixel_centers, positive_pixel_centers):
    for pixel_center in negative_pixel_centers:
        yield pixel_center
    point_rtree = RTree(positive_pixel_centers)
    while True:
        pixel_center = image_scope.get_random_pixel_center()
        # Retry if the pixel_frame contains a positive_pixel_center
        pixel_bounds = image_scope.get_pixel_bounds_from_pixel_center(
            pixel_center)
        if point_rtree.intersects(pixel_bounds):
            continue
        yield pixel_center
