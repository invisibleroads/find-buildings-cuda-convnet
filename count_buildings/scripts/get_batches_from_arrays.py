import sys
from crosscompute.libraries import script

from .get_arrays_from_image import ARRAYS_NAME
from .get_batches_from_datasets import save_meta, save_data
from ..libraries.dataset import BatchGroup


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--arrays_folder', metavar='FOLDER', required=True,
            help='')
        starter.add_argument(
            '--batch_size', metavar='SIZE', required=True,
            type=script.parse_size,
            help='maximum number of examples to include per batch')
        starter.add_argument(
            '--array_shape', metavar='HEIGHT,WIDTH,BAND_COUNT',
            type=script.parse_numbers,
            help='')


def run(
        target_folder, arrays_folder, batch_size, array_shape):
    batch_group = BatchGroup(ARRAYS_NAME, [arrays_folder], array_shape)
    keys = batch_group.get_random_keys(batch_size)
    save_meta(target_folder, batch_group, keys)
    batch_count = save_data(target_folder, batch_group, keys, batch_size)
    return dict(
        array_count=batch_group.array_count,
        array_shape=batch_group.array_shape,
        batch_count=batch_count,
        positive_count=sum(batch_group.get_labels(keys)))
