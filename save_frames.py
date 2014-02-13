import os
from argparse import ArgumentParser

from count_buildings.libraries.satellite_image import ImageScope


def run(
        target_folder,
        source_path,
        scope_dimensions,
        interval_dimensions):
    image_scope = ImageScope(source_path, scope_dimensions)
    interval_pixel_dimensions = image_scope.to_pixel_dimensions(
        interval_dimensions)
    for pixel_xy in image_scope.yield_pixel_xy(interval_pixel_dimensions):
        target_name = '%s-%s.jpg' % pixel_xy
        target_path = os.path.join(target_folder, target_name)
        image_scope.save_fixed_pixel_frame(target_path, pixel_xy)


def parse_dimensions(text):
    return [float(x) for x in text.split(',')]


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        'source_path')
    argument_parser.add_argument(
        '--target_folder',
        required=True,
        metavar='FOLDER')
    argument_parser.add_argument(
        '--scope_dimensions',
        metavar='WIDTH,HEIGHT',
        type=parse_dimensions,
        required=True,
        help='Dimensions of extracted image in geographic units')
    argument_parser.add_argument(
        '--interval_dimensions',
        metavar='WIDTH,HEIGHT',
        type=parse_dimensions,
        required=True,
        help='Dimensions of scanning interval in geographic units')
    arguments = argument_parser.parse_args()
    run(
        arguments.target_folder,
        arguments.source_path,
        arguments.scope_dimensions,
        arguments.interval_dimensions)
