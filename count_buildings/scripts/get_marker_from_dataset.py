import os
import sys
from crosscompute.libraries import script

from ..libraries.markers import initialize_marker
from ..libraries.dataset import DATASET_NAME


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--dataset_folder', metavar='FOLDER', required=True,
            help='selection of positive and negative examples')
        starter.add_argument(
            '--marker_module', metavar='PACKAGE', required=True,
            help='package path of classifier')
        starter.add_argument(
            '--cross_validate', action='store_true',
            help='evaluate marker parameters')


def run(target_folder, dataset_folder, marker_module, cross_validate):
    marker = initialize_marker(marker_module)
    dataset_path = os.path.join(dataset_folder, DATASET_NAME)
    if cross_validate:
        return marker.cross_validate(dataset_path)
    marker.calibrate(dataset_path)
    return marker.save(target_folder)
