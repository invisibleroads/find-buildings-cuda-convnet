import h5py
import numpy as np
import os
from functools import partial

from count_buildings.libraries import satellite_image
from count_buildings.libraries import script


def run(
        target_folder, image_path, tile_dimensions, overlap_dimensions,
        stay_inside_pixel_bounds, save_arrays, tile_indices):
    image_scope = satellite_image.ImageScope(image_path, tile_dimensions)
    interval_pixel_dimensions = image_scope.to_pixel_dimensions(
        tile_dimensions - overlap_dimensions)
    tile_packs = list(image_scope.yield_pixel_upper_left(
        interval_pixel_dimensions, stay_inside_pixel_bounds, tile_indices))
    tile_count = len(tile_packs)

    if save_arrays:
        save_tile = partial(save_array, *get_target_pack(
            target_folder, image_scope, tile_count, overlap_dimensions))
    else:
        save_tile = partial(save_image, target_folder, image_scope)

    for relative_index, tile_pack in enumerate(tile_packs):
        tile_index, pixel_upper_left = tile_pack
        array = image_scope.get_array_from_pixel_upper_left(pixel_upper_left)
        save_tile(tile_index, pixel_upper_left, relative_index, array)
    return dict(
        interval_pixel_dimensions=interval_pixel_dimensions,
        tile_count=tile_count,
        tile_pixel_dimensions=image_scope.scope_pixel_dimensions)


def get_target_pack(
        target_folder, image_scope, tile_count, overlap_dimensions):
    tile_dimensions = image_scope.scope_dimensions
    tile_h5 = get_tile_h5(target_folder, tile_dimensions, overlap_dimensions)
    tile_pixel_width, tile_pixel_height = image_scope.scope_pixel_dimensions
    arrays = tile_h5.create_dataset(
        'arrays', shape=(
            tile_count, tile_pixel_height, tile_pixel_width,
            image_scope.band_count), dtype=image_scope.array_dtype)
    pixel_upper_lefts = tile_h5.create_dataset(
        'pixel_upper_lefts', shape=(
            tile_count, 2), dtype=image_scope.pixel_dtype)
    tile_indices = tile_h5.create_dataset(
        'tile_indices', shape=(
            tile_count,), dtype=np.min_scalar_type(tile_count))
    return arrays, pixel_upper_lefts, tile_indices


def get_tile_h5(target_folder, tile_dimensions, overlap_dimensions):
    parts = ['t%dx%d' % tuple(tile_dimensions)]
    if overlap_dimensions is not None:
        parts.append('o%dx%d' % tuple(overlap_dimensions))
    name = '-'.join(parts)
    path = os.path.join(target_folder, name + '.h5')
    return h5py.File(path, 'w')


def save_array(
        arrays, pixel_upper_lefts, tile_indices,
        tile_index, pixel_upper_left, relative_index, array):
    arrays[relative_index, :, :, :] = array
    pixel_upper_lefts[relative_index, :] = pixel_upper_left
    tile_indices[relative_index] = tile_index


def save_image(
        target_folder, image_scope,
        tile_index, pixel_upper_left, relative_index, array):
    tile_path = get_tile_path(target_folder, tile_index, pixel_upper_left)
    image_scope.save_image(tile_path, array[:, :, :3])


def get_tile_path(target_folder, tile_index, pixel_upper_left):
    tile_name = '%s.jpg' % '-'.join([
        'i%d' % tile_index,
        'pul%dx%d' % pixel_upper_left,
    ])
    return os.path.join(target_folder, tile_name)


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        '--image_path', metavar='PATH', required=True,
        help='satellite image')
    argument_parser.add_argument(
        '--tile_dimensions', metavar='WIDTH,HEIGHT', required=True,
        type=script.parse_dimensions,
        help='dimensions of extracted tile in geographic units')
    argument_parser.add_argument(
        '--overlap_dimensions', metavar='WIDTH,HEIGHT', default=(0, 0),
        type=script.parse_dimensions,
        help='dimensions of tile overlap in geographic units')
    argument_parser.add_argument(
        '--stay_inside_pixel_bounds', metavar='MIN_X,MIN_Y,MAX_X,MAX_Y',
        type=script.parse_bounds,
        help='target specified bounds')
    argument_parser.add_argument(
        '--save_arrays', action='store_true',
        help='save arrays instead of images')
    argument_parser.add_argument(
        '--tile_indices', metavar='INTEGER,INTEGER,INTEGER',
        type=script.parse_numbers,
        help='indices to extract')
    arguments = script.parse_arguments(argument_parser)
    variables = run(**arguments.__dict__)
    script.save_run(arguments, variables, verbose=True)
