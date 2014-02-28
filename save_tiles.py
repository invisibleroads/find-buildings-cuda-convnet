import os

from count_buildings.libraries import satellite_image
from count_buildings.libraries import script


def run(
        target_folder,
        source_image_path,
        scope_dimensions,
        interval_dimensions):
    image_scope = satellite_image.ImageScope(
        source_image_path, scope_dimensions)
    interval_pixel_dimensions = image_scope.to_pixel_dimensions(
        interval_dimensions)
    for pixel_xy in image_scope.yield_pixel_xy(interval_pixel_dimensions):
        target_name = 'pixel-xy-%s-%s.jpg' % pixel_xy
        target_path = os.path.join(target_folder, target_name)
        image_scope.save_array_from_pixel_xy(target_path, pixel_xy)


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
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
        arguments.scope_dimensions,
        arguments.interval_dimensions)
