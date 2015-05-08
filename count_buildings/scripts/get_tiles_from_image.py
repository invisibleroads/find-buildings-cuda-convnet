import math
import sys
from crosscompute.libraries import script
from os.path import join

from ..libraries.satellite_image import SatelliteImage, MetricScope


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='satellite image')
        starter.add_argument(
            '--tile_metric_dimensions', metavar='WIDTH,HEIGHT',
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
        starter.add_argument(
            '--count_tiles', action='store_true',
            help='')


def run(
        target_folder, image_path,
        tile_metric_dimensions, overlap_metric_dimensions,
        tile_indices, count_tiles):
    if tile_metric_dimensions is None:
        return save_image_properties(image_path)
    elif count_tiles:
        return print_tile_count(
            image_path, tile_metric_dimensions, overlap_metric_dimensions,
            tile_indices)
    return save_tiles(
        target_folder, image_path,
        tile_metric_dimensions, overlap_metric_dimensions, tile_indices)


def save_image_properties(image_path):
    image = SatelliteImage(image_path)
    return dict(
        image_metric_dimensions=image.to_metric_dimensions(
            image.pixel_dimensions),
        image_pixel_dimensions=image.pixel_dimensions,
        image_band_count=image.band_count)


def print_tile_count(
        image_path, tile_metric_dimensions, overlap_metric_dimensions,
        tile_indices):
    image = SatelliteImage(image_path)
    image_scope = MetricScope(
        image, tile_metric_dimensions, overlap_metric_dimensions)
    print(image_scope.tile_count)


def save_tiles(
        target_folder, image_path,
        tile_metric_dimensions, overlap_metric_dimensions, tile_indices):
    image = SatelliteImage(image_path)
    image_scope = MetricScope(
        image, tile_metric_dimensions, overlap_metric_dimensions)
    maximum_tile_index = image_scope.tile_count - 1
    tile_path_template = get_tile_path_template(
        target_folder, maximum_tile_index)
    if not tile_indices:
        tile_indices = xrange(image_scope.tile_count)
    for tile_index in tile_indices:
        if tile_index > maximum_tile_index:
            break
        if tile_index % 100 == 0:
            print('%s / %s' % (tile_index, maximum_tile_index))
        pixel_frame = image_scope.get_pixel_frame_from_tile_index(
            tile_index)
        image_scope.render_array_from_pixel_frame(
            get_tile_path(tile_path_template, tile_index, pixel_frame),
            pixel_frame)
    print('%s / %s' % (maximum_tile_index, maximum_tile_index))
    return dict(
        tile_pixel_dimensions=image_scope.tile_pixel_dimensions,
        overlap_pixel_dimensions=image_scope.overlap_pixel_dimensions)


def get_tile_path_template(target_folder, maximum_tile_index):
    placeholder_count = int(math.floor(math.log10(maximum_tile_index))) + 1
    return join(target_folder, 'i%%0%dd-pul%%dx%%d.jpg' % placeholder_count)


def get_tile_path(path_template, tile_index, pixel_frame):
    pixel_upper_left = pixel_frame[0]
    return path_template % (
        tile_index, pixel_upper_left[0], pixel_upper_left[1])
