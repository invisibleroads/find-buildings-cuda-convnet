import h5py
import numpy as np
import os
import sys
from crosscompute.libraries import script

from .get_arrays_from_image import ARRAYS_NAME
from .get_batches_from_datasets import save_meta, save_data
from ..libraries.dataset import AbstractGroup
from ..libraries.satellite_image import get_pixel_center_from_pixel_frame


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
            type=script.parse_dimensions,
            help='')


def run(
        target_folder, arrays_folder, batch_size, array_shape):
    arrays_group = ArraysGroup([arrays_folder], array_shape)
    keys = arrays_group.get_keys()
    save_meta(target_folder, arrays_group, keys)
    save_data(target_folder, arrays_group, keys, batch_size)
    return dict(
        array_count=arrays_group.array_count,
        array_shape=arrays_group.array_shape)


class ArraysGroup(AbstractGroup):

    def __init__(self, arrays_folders, array_shape=None):
        self.h5s = [
            h5py.File(os.path.join(x, ARRAYS_NAME)) for x in dataset_folders]
        if array_shape:
            self._array_shape = array_shape

    def get_labels(self, keys):
        return np.zeros(len(keys))
