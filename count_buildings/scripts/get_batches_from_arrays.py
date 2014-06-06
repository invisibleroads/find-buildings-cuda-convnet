import numpy as np
import sys
from crosscompute.libraries import script
from progress.bar import Bar

from .get_arrays_from_image import ARRAYS_NAME
from .get_batches_from_datasets import save_meta, save_data
from ..libraries.dataset import AbstractGroup


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
    arrays_group = ArraysGroup([arrays_folder], array_shape)
    keys = arrays_group.get_keys()
    save_meta(target_folder, arrays_group, keys)
    batch_count = save_data(target_folder, arrays_group, keys, batch_size)
    return dict(
        array_count=arrays_group.array_count,
        array_shape=arrays_group.array_shape,
        batch_count=batch_count)


class ArraysGroup(AbstractGroup):

    H5_NAME = ARRAYS_NAME

    def get_labels(self, keys):
        return np.zeros(len(keys))
