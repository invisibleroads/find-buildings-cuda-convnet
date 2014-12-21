import h5py
import numpy as np
import sys
from crosscompute.libraries import script
from os.path import join

from .get_examples_from_points import get_pixel_centers
from ..libraries.kdtree import KDTree
from ..libraries.satellite_image import SatelliteImage, MetricScope
from ..libraries.satellite_image import get_pixel_center_from_pixel_frame


ARRAYS_NAME = 'arrays.h5'


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='satellite image')
        starter.add_argument(
            '--points_path', metavar='PATH',
            help='building locations')
        starter.add_argument(
            '--tile_metric_dimensions', metavar='WIDTH,HEIGHT', required=True,
            type=script.parse_dimensions,
            help='dimensions of extracted tile in metric units')
        starter.add_argument(
            '--overlap_metric_dimensions', metavar='WIDTH,HEIGHT',
            type=script.parse_dimensions, default=(0, 0),
            help='dimensions of tile overlap in metric units')
        starter.add_argument(
            '--tile_indices', metavar='INTEGER',
            type=script.parse_indices,
            help='comma-separated indices and ranges')


def run(
        target_folder, image_path, points_path,
        tile_metric_dimensions, overlap_metric_dimensions,
        tile_indices):
    return save_arrays(
        target_folder, image_path, points_path,
        tile_metric_dimensions, overlap_metric_dimensions, tile_indices)


def save_arrays(
        target_folder, image_path, points_path,
        tile_metric_dimensions, overlap_metric_dimensions, tile_indices):
    image = SatelliteImage(image_path)
    image_scope = MetricScope(
        image, tile_metric_dimensions, overlap_metric_dimensions)
    points_tree = KDTree(get_pixel_centers([
        points_path], image_scope)) if points_path else None
    maximum_tile_index = image_scope.tile_count - 1
    if not tile_indices:
        tile_indices = xrange(image_scope.tile_count)
    array_count = min(len(tile_indices), image_scope.tile_count)
    arrays, pixel_centers, labels = get_target_pack(
        target_folder, image_scope, array_count)
    for array_index, tile_index in enumerate(tile_indices):
        if tile_index > maximum_tile_index:
            break
        if array_index % 1000 == 0:
            print('%s / %s' % (array_index, array_count - 1))
        pixel_frame = image_scope.get_pixel_frame_from_tile_index(
            tile_index)
        arrays[array_index, :, :, :] = image_scope.get_array_from_pixel_frame(
            pixel_frame)
        pixel_centers[array_index, :] = get_pixel_center_from_pixel_frame(
            pixel_frame)
        labels[array_index] = get_label(points_tree, pixel_frame)
    print('%s / %s' % (array_count - 1, array_count - 1))
    return dict(
        tile_pixel_dimensions=image_scope.tile_pixel_dimensions,
        overlap_pixel_dimensions=image_scope.overlap_pixel_dimensions,
        array_count=array_count,
        positive_fraction=np.sum(labels) / float(array_count))


def get_target_pack(target_folder, image_scope, array_count):
    tile_pixel_width, tile_pixel_height = image_scope.tile_pixel_dimensions
    arrays_h5 = get_arrays_h5(target_folder)
    arrays = arrays_h5.create_dataset(
        'arrays', shape=(
            array_count, tile_pixel_height, tile_pixel_width,
            image_scope.band_count), dtype=image_scope.array_dtype)
    pixel_centers = arrays_h5.create_dataset(
        'pixel_centers', shape=(
            array_count, 2), dtype=image_scope.pixel_coordinate_dtype)
    pixel_centers.attrs['calibration_pack'] = image_scope.calibration_pack
    pixel_centers.attrs['proj4'] = image_scope.proj4
    labels = arrays_h5.create_dataset(
        'labels', shape=(array_count,), dtype=bool)
    return arrays, pixel_centers, labels


def get_arrays_h5(target_folder):
    return h5py.File(join(target_folder, ARRAYS_NAME), 'w')


def get_label(points_tree, pixel_frame):
    if not points_tree:
        return False
    pixel_center = get_pixel_center_from_pixel_frame(
        pixel_frame)
    pixel_dimensions = pixel_frame[1]
    pixel_radius = max(pixel_dimensions) / 2.
    indices = points_tree.query(
        pixel_center,
        maximum_count=1,
        maximum_distance=pixel_radius)[1]
    return True if indices else False
