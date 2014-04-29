import h5py
import os
from decorator import decorator

from . import disk


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
