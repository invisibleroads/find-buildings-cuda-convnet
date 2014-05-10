import h5py

from .. import dataset
from .. import disk


keep_array_shape = lambda array_shape: array_shape
keep_array = lambda array: array
keep_label_shape = lambda label_shape: label_shape
keep_label = lambda label: label


def prepare_arrays_and_labels(
        dataset_path, suffix,
        get_array_shape=keep_array_shape, get_array=keep_array,
        get_label_shape=keep_label_shape, get_label=keep_label):
    source_arrays, source_labels = dataset.load_arrays_and_labels(dataset_path)
    target_dataset_path = disk.suffix_name(dataset_path, suffix)
    target_dataset_h5 = h5py.File(target_dataset_path, 'w')

    target_arrays = target_dataset_h5.create_dataset(
        'arrays',
        shape=(len(source_arrays),) + get_array_shape(source_arrays.shape[1:]),
        dtype=source_arrays.dtype)
    for index, source_array in enumerate(source_arrays):
        target_arrays[index] = get_array(source_array)

    target_labels = target_dataset_h5.create_dataset(
        'labels',
        shape=(len(source_labels),) + get_label_shape(source_labels.shape[1:]),
        dtype=source_labels.dtype)
    for index, source_label in enumerate(source_labels):
        target_labels[index] = get_label(source_label)

    target_dataset_h5.close()
    return target_dataset_path
