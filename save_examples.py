import h5py
import operator
import os
import rtree
from geometryIO import get_transformPoint, load_points
from scipy.sparse import lil_matrix

from count_buildings.libraries import calculator
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
        target_folder,
        source_image_path,
        source_point_path,
        scope_dimensions,
        save_images,
        is_test):
    image_scope = satellite_image.ImageScope(
        source_image_path, scope_dimensions)
    point_proj4, positive_centers = load_points(source_point_path)[:2]
    transform_point = get_transformPoint(point_proj4, image_scope.proj4)

    target_path = os.path.normpath(target_folder) + '.h5'
    target_h5 = h5py.File(target_path, 'w')

    def save_example(target_folder, pixel_center, array):
        target_name = 'pixel-center-%s-%s.jpg' % tuple(pixel_center)
        target_path = os.path.join(target_folder, target_name)
        image_scope.save_array(target_path, array[:, :, :3])

    positive_count = 1 if is_test else len(positive_centers)
    print 'positive_count = %s' % positive_count

    positive_pixel_centers = []
    positive_arrays = []
    positives_folder = os.path.join(target_folder, 'positives')
    try:
        os.makedirs(positives_folder)
    except OSError:
        pass
    for positive_index in xrange(positive_count):
        center = positive_centers[positive_index]
        # Transform center into spatial reference of image
        transformed_center = transform_point(*center)
        pixel_center = image_scope.to_pixel_xy(transformed_center)
        positive_pixel_centers.append(pixel_center)
        # Get array
        array = image_scope.get_array_from_pixel_center(pixel_center)
        positive_arrays.append(array)
        if save_images:
            save_example(positives_folder, pixel_center, array)
    target_h5.create_dataset(
        'positive/pixel_centers', data=positive_pixel_centers)
    target_h5.create_dataset(
        'positive/arrays', data=positive_arrays)

    negative_count = 1 if is_test else estimate_negative_count(
        image_scope, positive_pixel_centers)
    print 'negative_count = %s' % negative_count

    negative_pixel_centers = []
    negative_arrays = []
    negatives_folder = os.path.join(target_folder, 'negatives')
    try:
        os.makedirs(negatives_folder)
    except OSError:
        pass
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
        negative_arrays.append(array)
        if save_images:
            save_example(negatives_folder, pixel_center, array)
    target_h5.create_dataset(
        'negative/pixel_centers', data=negative_pixel_centers)
    target_h5.create_dataset(
        'negative/arrays', data=negative_arrays)


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


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        'source_point_path')
    argument_parser.add_argument(
        '--save_images',
        action='store_true',
        help='save images of positive and negative examples')
    argument_parser.add_argument(
        '--test',
        action='store_true',
        help='save one positive example and one negative example')
    arguments = script.parse_arguments(argument_parser)
    run(
        arguments.target_folder,
        arguments.source_image_path,
        arguments.source_point_path,
        arguments.scope_dimensions,
        arguments.save_images,
        arguments.test)
