import os
from argparse import ArgumentParser
from count_buildings.libraries.disk import make_folder
from count_buildings.scripts import get_examples_from_points
from glob import glob
from os.path import basename, dirname, exists, join
from pandas import read_csv


EXAMPLES_FOLDER = join('/tmp', get_basename(__file__))


def run(target_link_folder, source_image_folder, source_table_path):
    source_table = read_csv(source_table_path)


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
            join()
            target_example_folder, source_image_path, source_shapefile_path)


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
    make_folder(target_folder)
    os.chdir(target_folder)
    if exists(target_path):
        os.remove(target_path)
    os.symlink(source_path, basename(target_path))
    return target_path


def save_examples(target_folder, image_path, shapefile_path):
    get_examples_from_points.run(
            
    )

    get_examples_from_points \
        --target_folder /tmp/get_examples_from_points/$IMAGE_NAME \
        --image_path ~/Links/satellite-images/$IMAGE_NAME \
        --example_metric_dimensions 16x16 \
        --positive_points_paths ~/Links/building-locations/$IMAGE_NAME \
        --maximum_positive_count 10 \
        --maximum_negative_count 10 \
        --save_images
def run(
        target_folder, image_path, example_metric_dimensions,
        positive_points_paths, negative_points_paths,
        maximum_positive_count, maximum_negative_count, save_images):


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_link_folder', metavar='FOLDER', required=True)
    argument_parser.add_argument(
        '--source_image_folder', metavar='FOLDER', required=True)
    argument_parser.add_argument(
        '--source_table_path', metavar='PATH', required=True)
    arguments = argument_parser.parse_args()
    run(
        arguments.target_link_folder,
        arguments.source_image_folder,
        arguments.source_table_path)
