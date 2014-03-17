import os

from count_buildings.libraries import disk
from count_buildings.libraries import satellite_image
from count_buildings.libraries import script


def run(
        target_folder,
        source_image_path, tile_indices, tile_dimensions, interval_dimensions):
    target_tile_folder = make_tile_folder(
        target_folder, tile_dimensions, interval_dimensions)

    image_scope = satellite_image.ImageScope(
        source_image_path, tile_dimensions)
    interval_pixel_dimensions = image_scope.to_pixel_dimensions(
        interval_dimensions)
    pixel_xy_iter = image_scope.yield_pixel_xy(interval_pixel_dimensions)

    for pixel_index, pixel_xy in enumerate(pixel_xy_iter):
        if tile_indices and pixel_index not in tile_indices:
            continue
        target_tile_path = get_tile_path(target_tile_folder, pixel_xy)
        image_scope.save_array_from_pixel_xy(target_tile_path, pixel_xy)


def make_tile_folder(target_folder, tile_dimensions, interval_dimensions):
    tile_folder_name = '-'.join([
        't%dx%d' % tuple(tile_dimensions),
        'i%dx%d' % tuple(interval_dimensions)])
    return disk.replace_folder(target_folder, tile_folder_name)


def get_tile_path(target_folder, pixel_xy):
    tile_name = 'pixel-xy-%s-%s.jpg' % pixel_xy
    return os.path.join(target_folder, tile_name)


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        'source_image_path')
    argument_parser.add_argument(
        '--tile_indices',
        metavar='0,1,2',
        type=script.parse_numbers,
        help='indices to extract')
    argument_parser.add_argument(
        '--tile_dimensions',
        metavar='WIDTH,HEIGHT',
        required=True,
        type=script.parse_dimensions,
        help='dimensions of extracted tile in geographic units')
    argument_parser.add_argument(
        '--interval_dimensions',
        metavar='WIDTH,HEIGHT',
        required=True,
        type=script.parse_dimensions,
        help='dimensions of scanning interval in geographic units')
    arguments = script.parse_arguments(argument_parser)
    run(
        arguments.target_folder,
        arguments.source_image_path,
        arguments.tile_indices,
        arguments.tile_dimensions,
        arguments.interval_dimensions)
