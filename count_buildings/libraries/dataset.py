import h5py
import numpy as np
import operator
import os
from decorator import decorator
from skimage.transform import resize

from . import disk


DATASET_NAME = 'dataset.h5'


class AbstractGroup(object):

    def get_keys(self):
        keys = []
        for h5_index, h5 in enumerate(self.h5s):
            keys.extend((
                h5_index, array_index
            ) for array_index in xrange(len(h5['arrays'])))
        return keys

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
        self._array_shape = selected_height, selected_width, selected_band_count
        return self._array_shape

    @property
    def array_count(self):
        try:
            return self._array_count
        except AttributeError:
            pass
        array_count = 0
        for h5_index, h5 in enumerate(self.h5s):
            arrays = h5['arrays']
            array_count += len(arrays)
        self._array_count = array_count
        return self._array_count

    @property
    def array_mean(self):
        try:
            return self._array_mean
        except AttributeError:
            pass
        array_sum = 0
        for h5_index, h5 in enumerate(self.h5s):
            arrays = h5['arrays']
            if arrays.shape[1:] == self.array_shape:
                array_sum += np.sum(arrays, axis=0)
            else:
                array_sum += reduce(operator.add, (
                    self.resize_array(x) for x in arrays))
        self._array_mean = array_sum / float(self.array_count)
        return self._array_mean

    @property
    def array_sd(self):
        try:
            return self._array_sd
        except AttributeError:
            pass
        get_squared_difference = lambda x: (x - self.array_mean) ** 2
        squared_difference_sum = 0
        for h5_index, h5 in enumerate(self.h5s):
            arrays = h5['arrays']
            if arrays.shape[1:] == self.array_shape:
                squared_difference_sum += np.sum(
                    get_squared_difference(arrays), axis=0)
            else:
                squared_difference_sum += reduce(operator.add, (
                    get_squared_difference(
                        self.resize_array(x)) for x in arrays))
        variance = squared_difference_sum / float(self.array_count)
        self._array_sd = np.sqrt(variance)
        return self._array_sd

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
        if array.shape == self.array_shape:
            return array
        assert pixel_height <= array.shape[0] and pixel_width <= array.shape[1]
        return resize(array, (pixel_height, pixel_width)) * 255


class DatasetGroup(AbstractGroup):

    def __init__(self, dataset_folders):
        self.h5s = [
            h5py.File(os.path.join(x, DATASET_NAME)) for x in dataset_folders]

    def get_labels(self, keys):
        labels = []
        for h5_index, array_index in keys:
            h5 = self.h5s[h5_index]
            label = h5['labels'][array_index]
            labels.append(label)
        return labels


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
