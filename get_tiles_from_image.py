import os

from count_buildings.libraries import satellite_image
from count_buildings.libraries import script


def run(
        target_folder,
        image_path, tile_dimensions, overlap_dimensions, tile_indices):
    image_scope = satellite_image.ImageScope(image_path, tile_dimensions)
    interval_pixel_dimensions = image_scope.to_pixel_dimensions(
        tile_dimensions - overlap_dimensions)
    for tile_index, pixel_upper_left in enumerate(
            image_scope.yield_pixel_upper_left(interval_pixel_dimensions)):
        if tile_indices and tile_index not in tile_indices:
            continue
        tile_path = get_tile_path(target_folder, tile_index, pixel_upper_left)
        image_scope.save_array_from_pixel_upper_left(
            tile_path, pixel_upper_left)
    return dict(
        interval_pixel_dimensions=interval_pixel_dimensions)


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
        '--tile_indices', metavar='INTEGER,INTEGER',
        type=script.parse_numbers,
        help='indices to extract')
    arguments = script.parse_arguments(argument_parser)
    variables = run(**arguments.__dict__)
    script.save_run(arguments, variables, verbose=True)
