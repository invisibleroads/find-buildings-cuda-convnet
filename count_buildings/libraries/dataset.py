import h5py
import numpy as np
import operator
import os
from decorator import decorator
from random import shuffle
from scipy.ndimage.interpolation import zoom

from . import disk


pil_mode_by_array_dtype = {
    np.dtype('uint8'): None,
    np.dtype('uint16'): 'I;16',
}


class BatchGroup(object):

    def __init__(self, h5_name, h5_folders, batch_size, array_shape=None):
        self.h5s = [
            h5py.File(os.path.join(x, h5_name)) for x in h5_folders]
        self.batch_size = batch_size
        if array_shape is not None:
            self._array_shape = tuple(array_shape)

    @property
    def keys(self):
        try:
            return self._keys
        except AttributeError:
            pass
        keys = []
        for h5_index, h5 in enumerate(self.h5s):
            arrays = h5['arrays']
            for array_index in xrange(len(arrays)):
                # Skip empty arrays
                if arrays[array_index].max() == 0:
                    continue
                keys.append((h5_index, array_index))
        # Use existing keys as filler to make the last batch whole
        while True:
            extra_size = len(keys) % self.batch_size
            if not extra_size:
                break
            keys += keys[:self.batch_size - extra_size]
        shuffle(keys)
        self._keys = keys
        return self._keys

    def get_labels(self, keys):
        labels = []
        for h5_index, array_index in keys:
            h5 = self.h5s[h5_index]
            label = h5['labels'][array_index]
            labels.append(label)
        return labels

    @property
    def array_shape(self):
        try:
            return self._array_shape
        except AttributeError:
            pass
        selected_height = np.inf
        selected_width = np.inf
        selected_band_count = np.inf
        for h5_index, h5 in enumerate(self.h5s):
            arrays = h5['arrays']
            pixel_height, pixel_width, band_count = arrays.shape[1:]
            if pixel_height * pixel_width < selected_height * selected_width:
                selected_height, selected_width = pixel_height, pixel_width
            if band_count < selected_band_count:
                selected_band_count = band_count
        self._array_shape = (
            selected_height, selected_width, selected_band_count)
        return self._array_shape

    @property
    def array_count(self):
        try:
            return self._array_count
        except AttributeError:
            pass
        self._array_count = len(self.keys)
        return self._array_count

    @property
    def array_mean(self):
        try:
            return self._array_mean
        except AttributeError:
            pass
        if not self.array_count:
            return np.zeros(self.array_shape)
        array_sum = 0
        for h5_index, h5 in enumerate(self.h5s):
            arrays = h5['arrays']
            array_sum += reduce(operator.add, (
                self.resize_array(x) for x in arrays))
        self._array_mean = array_sum / float(self.array_count)
        return self._array_mean

    def get_pixel_centers(self, keys):
        pixel_centers = []
        for h5_index, array_index in keys:
            h5 = self.h5s[h5_index]
            pixel_center = h5['pixel_centers'][array_index]
            pixel_centers.append(pixel_center)
        return pixel_centers

    def get_data(self, keys):
        vectors = []
        for h5_index, array_index in keys:
            h5 = self.h5s[h5_index]
            array = h5['arrays'][array_index]
            vectors.append(get_vector_from_array(self.resize_array(array)))
        return np.array(vectors).T

    def resize_array(self, array):
        pixel_height, pixel_width, band_count = self.array_shape
        assert band_count <= array.shape[2]
        array = array[:, :, :band_count]
        if tuple(array.shape) == tuple(self.array_shape):
            return array
        return zoom(array, (
            pixel_height / float(array.shape[0]),
            pixel_width / float(array.shape[1]),
            1))


@decorator
def skip_if_exists(f, *args, **kw):
    target_dataset_path = disk.suffix_name(*args, **kw)
    if os.path.exists(target_dataset_path):
        return target_dataset_path
    return f(*args, **kw)


def load_arrays_and_labels(dataset_path):
    dataset_h5 = h5py.File(dataset_path, 'r')
    return dataset_h5['arrays'], dataset_h5['labels']


def load_arrays(arrays_path):
    dataset_h5 = h5py.File(arrays_path, 'r')
    return dataset_h5['arrays']


def get_vector_from_array(array):
    return array.swapaxes(0, 2).swapaxes(1, 2).ravel()


def get_vectors_from_arrays(arrays):
    return arrays.swapaxes(1, 3).swapaxes(2, 3).reshape((arrays.shape[0], -1))
