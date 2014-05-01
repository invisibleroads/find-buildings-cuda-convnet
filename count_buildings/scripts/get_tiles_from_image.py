import os
import sys
import numpy as np
from crosscompute.libraries import script

from count_buildings.libraries import satellite_image


def go(argv=sys.argv):
    argument_parser = script.get_argument_parser(__file__)
    argument_parser.add_argument(
        '--image_path', metavar='PATH', required=True,
        help='satellite image')
    argument_parser.add_argument(
        '--tile_dimensions', metavar='WIDTH,HEIGHT',
        type=script.parse_dimensions,
        help='dimensions of extracted tile in geographic units')
    argument_parser.add_argument(
        '--overlap_dimensions', metavar='WIDTH,HEIGHT', default=(0, 0),
        type=script.parse_dimensions,
        help='dimensions of tile overlap in geographic units')
    argument_parser.add_argument(
        '--tile_indices', metavar='INTEGER,INTEGER,INTEGER',
        type=script.parse_numbers,
        help='indices to extract')
    argument_parser.add_argument(
        '--included_pixel_bounds', metavar='MIN_X,MIN_Y,MAX_X,MAX_Y',
        type=script.parse_bounds,
        help='target specified bounds')
    arguments = script.parse_arguments(argument_parser, argv)
    variables = run(**arguments.__dict__)
    script.save_run(arguments, variables)


def run(
        target_folder, image_path,
        tile_dimensions, overlap_dimensions, tile_indices,
        included_pixel_bounds):
    if tile_dimensions is None and included_pixel_bounds is None:
        return save_image_dimensions(image_path)
    elif tile_dimensions is None:
        return save_pixel_bounds(
            target_folder, image_path, included_pixel_bounds)
    return save_tiles(
        target_folder, image_path,
        tile_dimensions, overlap_dimensions, tile_indices,
        included_pixel_bounds)


def save_image_dimensions(image_path):
    image = satellite_image.SatelliteImage(image_path)
    return dict(
        image_dimensions=image.to_dimensions(image.pixel_dimensions),
        image_pixel_dimensions=image.pixel_dimensions)


def save_pixel_bounds(
        target_folder, image_path, included_pixel_bounds):
    image = satellite_image.SatelliteImage(image_path)
    minimum_x, minimum_y, maximum_x, maximum_y = included_pixel_bounds
    tile_pixel_dimensions = np.array([
        (maximum_x - minimum_x),
        (maximum_y - minimum_y),
    ])
    tile_dimensions = image.to_dimensions(tile_pixel_dimensions)
    pixel_upper_left = minimum_x, minimum_y
    # Save
    target_path = get_tile_path(target_folder, pixel_upper_left)
    pixel_frame = pixel_upper_left, tile_pixel_dimensions
    image.save_image_from_pixel_frame(target_path, pixel_frame)
    return dict(
        tile_dimensions=tile_dimensions,
        tile_pixel_dimensions=tile_pixel_dimensions)


def save_tiles(
        target_folder, image_path,
        tile_dimensions, overlap_dimensions, tile_indices,
        included_pixel_bounds):
    image_scope = satellite_image.ImageScope(image_path, tile_dimensions)
    tile_packs = image_scope.yield_tile_pack(
        overlap_dimensions, included_pixel_bounds, tile_indices)
    for tile_index, pixel_upper_left in tile_packs:
        array = image_scope.get_array_from_pixel_upper_left(pixel_upper_left)
        image_scope.save_image(
            get_tile_path(target_folder, pixel_upper_left, tile_index),
            array[:, :, :3])
    return dict(
        tile_pixel_dimensions=image_scope.scope_pixel_dimensions,
        overlap_pixel_dimensions=image_scope.to_pixel_dimensions(
            overlap_dimensions))


def get_tile_path(target_folder, pixel_upper_left, tile_index=None):
    tile_name_parts = ['pul%dx%d' % pixel_upper_left]
    if tile_index is not None:
        tile_name_parts.append('i%d' % tile_index)
    tile_name = '%s.jpg' % '-'.join(tile_name_parts)
    return os.path.join(target_folder, tile_name)
