import os
import shutil
from argparse import ArgumentParser
from count_buildings.scripts import get_examples_from_points
from crosscompute.libraries import disk, script
from glob import glob
from os.path import basename, dirname, exists, join
from pandas import read_csv


def run(
        target_link_folder, source_image_folder, source_table_path,
        example_metric_dimensions,
        maximum_positive_count, maximum_negative_count):
    source_table = read_csv(source_table_path)
    target_examples_folder = prepare_examples_folder(__file__)
    for row_index, row in source_table.iterrows():
        source_nickname = row['nickname']
        print(source_nickname)
        source_image_path = join(source_image_folder, row['relative_path'])
        image_link_path = make_link(
            join(target_link_folder, 'satellite-images', source_nickname),
            source_image_path)
        print('--> %s' % image_link_path)
        try:
            source_shapefile_path = find_shapefile_path(source_image_path)
        except IndexError:
            continue
        shapefile_link_path = make_link(
            join(target_link_folder, 'building-locations', source_nickname),
            source_shapefile_path)
        print('--> %s' % shapefile_link_path)
        save_examples(
            target_examples_folder, source_image_path, source_shapefile_path,
            example_metric_dimensions,
            maximum_positive_count, maximum_negative_count)


def prepare_examples_folder(script_path):
    examples_folder = join('/tmp', disk.get_basename(script_path))
    shutil.rmtree(examples_folder, ignore_errors=True)
    disk.make_folder(examples_folder)
    return examples_folder


def find_shapefile_path(image_path):
    base_folder = dirname(find_parent_folder('Images', image_path))
    shapefile_folder = join(base_folder, 'Features', 'Buildings', 'Interim')
    return glob(join(shapefile_folder, '*.shp'))[0]


def find_parent_folder(folder_name, file_path):
    current_folder = dirname(file_path)
    while basename(current_folder) != folder_name:
        parent_folder = dirname(current_folder)
        if parent_folder == current_folder:
            raise KeyError
        current_folder = parent_folder
    return current_folder


def make_link(target_path, source_path):
    target_folder = dirname(target_path)
    disk.make_folder(target_folder)
    os.chdir(target_folder)
    if exists(target_path):
        os.remove(target_path)
    os.symlink(source_path, basename(target_path))
    return target_path


def save_examples(
        target_folder, image_path, shapefile_path,
        example_metric_dimensions,
        maximum_positive_count, maximum_negative_count):
    get_examples_from_points.run(
        target_folder, image_path,
        positive_points_paths=[shapefile_path],
        negative_points_paths=[None],
        example_metric_dimensions=example_metric_dimensions,
        maximum_positive_count=maximum_positive_count,
        maximum_negative_count=maximum_negative_count,
        save_images=True)


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_link_folder', metavar='FOLDER',
        required=True)
    argument_parser.add_argument(
        '--source_image_folder', metavar='FOLDER',
        required=True)
    argument_parser.add_argument(
        '--source_table_path', metavar='PATH',
        required=True)
    argument_parser.add_argument(
        '--example_metric_dimensions', metavar='WIDTH,HEIGHT',
        type=script.parse_dimensions, required=True)
    argument_parser.add_argument(
        '--maximum_positive_count', metavar='INTEGER',
        type=script.parse_size, default=10,
        help='maximum number of positive examples to extract')
    argument_parser.add_argument(
        '--maximum_negative_count', metavar='INTEGER',
        type=script.parse_size, default=10,
        help='maximum number of negative examples to extract')
    arguments = argument_parser.parse_args()
    run(
        arguments.target_link_folder,
        arguments.source_image_folder,
        arguments.source_table_path)
