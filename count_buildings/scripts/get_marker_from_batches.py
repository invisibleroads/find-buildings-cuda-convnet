import math
import sys
from crosscompute.libraries import script

from ..libraries.dataset import get_batch_range
from ..libraries.markers.ccn import ConvNet, get_model_arguments


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--batch_folder', metavar='FOLDER', required=True,
            help='')
        starter.add_argument(
            '--testing_fraction', metavar='FRACTION',
            type=float, default=0.2,
            help='')
        starter.add_argument(
            '--data_provider', metavar='DATA-PROVIDER', required=True,
            help='')
        starter.add_argument(
            '--crop_border_pixel_length', metavar='INTEGER',
            type=int,
            help='')
        starter.add_argument(
            '--layer_definition_path', metavar='PATH', required=True,
            help='')
        starter.add_argument(
            '--layer_parameters_path', metavar='PATH', required=True,
            help='')
        starter.add_argument(
            '--patience_epoch_count', metavar='INTEGER',
            type=int, default=100,
            help='')


def run(
        target_folder, batch_folder, testing_fraction,
        data_provider, crop_border_pixel_length,
        layer_definition_path, layer_parameters_path,
        patience_epoch_count):
    batch_range = get_batch_range(batch_folder)
    training_batch_range, testing_batch_range = split_range(
        batch_range, testing_fraction)
    model_arguments = get_model_arguments(
        target_folder, batch_folder,
        training_batch_range, testing_batch_range,
        data_provider, crop_border_pixel_length,
        layer_definition_path, layer_parameters_path,
        patience_epoch_count)
    model = ConvNet(*model_arguments)
    model.start()
    return dict(
        training_batch_range=training_batch_range,
        testing_batch_range=testing_batch_range,
        testing_error=model.get_var('best_test_error'))


def split_range(batch_range, testing_fraction):
    max_batch_range = max(batch_range)
    min_batch_range = min(batch_range)
    batch_count = max_batch_range - min_batch_range + 1
    testing_count = int(math.ceil(batch_count * testing_fraction))
    training_batch_range = min_batch_range, max_batch_range - testing_count
    testing_batch_range = max_batch_range - testing_count + 1, max_batch_range
    return training_batch_range, testing_batch_range
