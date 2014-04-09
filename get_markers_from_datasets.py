import datetime
import h5py
import os
from importlib import import_module

from count_buildings.libraries import disk
from count_buildings.libraries import script


MARKERS_FOLDER = 'count_buildings.libraries.markers'


def run(target_folder, dataset_path, marker_module):
    dataset_h5 = h5py.File(dataset_path, 'r')
    dataset_arrays = dataset_h5['arrays']
    dataset_labels = dataset_h5['labels']

    marker = get_marker(marker_module, target_folder)
    marker.calibrate(dataset_arrays, dataset_labels)
    marker.save(target_folder)
    return dict()


def get_marker(marker_module, target_folder):
    marker_module = import_module(MARKERS_FOLDER + '.' + marker_module)
    return marker_module.Marker(target_folder)


def get_marker_name(dataset_path):
    parts = [
        disk.get_basename(dataset_path),
        datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
    ]
    return '-'.join(parts)


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        'dataset_path')
    argument_parser.add_argument(
        'marker_module')
    arguments = script.parse_arguments(argument_parser)
    variables = run(**arguments.__dict__)
    script.save_run(arguments, variables, verbose=True)
