import h5py
import operator
import os
import rtree
from geometryIO import get_transformPoint, load_points
from scipy.sparse import lil_matrix

from count_buildings.libraries import calculator
from count_buildings.libraries import disk
from count_buildings.libraries import satellite_image
from count_buildings.libraries import script


class PointTree(object):

    def __init__(self, points):
        self.rtree = rtree.index.Index()
        for index, point in enumerate(points):
            self.rtree.insert(index, tuple(point))

    def intersects(self, bounds):
        try:
            self.rtree.intersection(bounds).next()
        except StopIteration:
            return False
        else:
            return True


def run(
        target_folder, source_image_path, source_point_path,
        example_dimensions, positive_count, negative_count, save_images):
    image_scope = satellite_image.ImageScope(
        source_image_path, example_dimensions)
    example_pixel_dimensions = image_scope.scope_pixel_dimensions
    point_proj4, positive_centers = load_points(source_point_path)[:2]
    transform_point = get_transformPoint(point_proj4, image_scope.proj4)
    positive_pixel_centers = [
        image_scope.to_pixel_xy(transform_point(*_)) for _ in positive_centers]
    example_folder = get_example_folder(target_folder, example_dimensions)
    example_h5 = get_example_h5(example_folder)

    if positive_count is None:
        positive_count = len(positive_pixel_centers)
    print 'positive_count = %s' % positive_count
    if negative_count is None:
        negative_count = estimate_negative_count(
            image_scope, positive_pixel_centers)
    print 'negative_count = %s' % negative_count

    save_positive_examples(
        example_h5, example_folder, example_pixel_dimensions,
        image_scope, positive_pixel_centers, positive_count, save_images)
    save_negative_examples(
        example_h5, example_folder, example_pixel_dimensions,
        image_scope, positive_pixel_centers, negative_count, save_images)


def get_example_folder(target_folder, example_dimensions):
    example_folder_name = 'e%dx%d' % tuple(example_dimensions)
    return os.path.join(target_folder, example_folder_name)


def get_example_h5(example_folder):
    file_path = os.path.normpath(example_folder) + '.h5'
    return h5py.File(file_path, 'w')


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
        example_h5, example_folder,
        (example_pixel_width, example_pixel_height),
        image_scope, positive_pixel_centers, positive_count, save_images):
    if save_images:
        positives_folder = disk.replace_folder(example_folder, 'positives')
    positive_arrays = example_h5.create_dataset(
        'positive/arrays', shape=(
            positive_count, example_pixel_height, example_pixel_width,
            image_scope.band_count))
    for positive_index in xrange(positive_count):
        pixel_center = positive_pixel_centers[positive_index]
        # Get array
        array = image_scope.get_array_from_pixel_center(pixel_center)
        positive_arrays[positive_index, :, :, :] = array
        if save_images:
            save_example(image_scope, positives_folder, pixel_center, array)
    example_h5.create_dataset(
        'positive/pixel_centers', data=positive_pixel_centers)
    return positive_pixel_centers


def save_negative_examples(
        example_h5, example_folder,
        (example_pixel_width, example_pixel_height),
        image_scope, positive_pixel_centers, negative_count, save_images):
    if save_images:
        negatives_folder = disk.replace_folder(example_folder, 'negatives')
    negative_pixel_centers = []
    negative_arrays = example_h5.create_dataset(
        'negative/arrays', shape=(
            negative_count, example_pixel_height, example_pixel_width,
            image_scope.band_count))
    point_tree = PointTree(positive_pixel_centers)
    for negative_index in xrange(negative_count):
        # Get random pixel_center
        pixel_center = image_scope.get_random_pixel_center()
        # Convert pixel_center to pixel_bounds
        pixel_bounds = image_scope.get_pixel_bounds_from_pixel_center(
            pixel_center)
        # Retry if the pixel_frame contains a positive_pixel_center
        if point_tree.intersects(pixel_bounds):
            continue
        negative_pixel_centers.append(pixel_center)
        # Get array
        array = image_scope.get_array_from_pixel_center(pixel_center)
        negative_arrays[negative_index, :, :, :] = array
        if save_images:
            save_example(image_scope, negatives_folder, pixel_center, array)
    example_h5.create_dataset(
        'negative/pixel_centers', data=negative_pixel_centers)
    return negative_pixel_centers


def save_example(image_scope, target_folder, pixel_center, array):
    example_path = get_example_path(target_folder, pixel_center)
    image_scope.save_array(example_path, array[:, :, :3])


def get_example_path(target_folder, pixel_center):
    example_file_name = 'pixel-center-%s-%s.jpg' % tuple(pixel_center)
    return os.path.join(target_folder, example_file_name)


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        'source_image_path')
    argument_parser.add_argument(
        'source_point_path')
    argument_parser.add_argument(
        '--example_dimensions',
        metavar='WIDTH,HEIGHT',
        required=True,
        type=script.parse_dimensions,
        help='dimensions of extracted example in geographic units')
    argument_parser.add_argument(
        '--positive_count',
        type=int,
        help='maximum number of positive examples to extract')
    argument_parser.add_argument(
        '--negative_count',
        type=int,
        help='maximum number of negative examples to extract')
    argument_parser.add_argument(
        '--save_images',
        action='store_true',
        help='save images of positive and negative examples')
    arguments = script.parse_arguments(argument_parser)
    run(
        arguments.target_folder,
        arguments.source_image_path,
        arguments.source_point_path,
        arguments.example_dimensions,
        arguments.positive_count,
        arguments.negative_count,
        arguments.save_images)
