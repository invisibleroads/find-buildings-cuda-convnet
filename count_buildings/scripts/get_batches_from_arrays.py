import h5py
import os
import sys
from crosscompute.libraries import script

from .get_arrays_from_image import ARRAYS_NAME
from .get_batches_from_dataset import save_meta, save_data
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


def run(
        target_folder, arrays_folder, batch_size):
    arrays_h5 = h5py.File(os.path.join(arrays_folder, ARRAYS_NAME))
    arrays = arrays_h5['arrays'].value
    array_shape = pixel_height, pixel_width, band_count = arrays.shape[1:]

    vectors = arrays.swapaxes(1, 3).swapaxes(2, 3).reshape((
        arrays.shape[0], -1))
    label_names = ['', 'building']
    pixel_upper_lefts = arrays_h5['pixel_upper_lefts']
    pixel_dimensions = pixel_width, pixel_height
    pixel_centers = [get_pixel_center_from_pixel_frame(
        (_, pixel_dimensions)) for _ in pixel_upper_lefts]

    save_meta(target_folder, vectors, label_names, pixel_centers, array_shape)
    save_data(target_folder, vectors, [], batch_size)
