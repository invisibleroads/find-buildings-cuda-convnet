import operator

from . import prepare_arrays_and_labels
from .. import dataset


@dataset.skip_if_exists
def flatten(dataset_path, suffix='flattened'):
    return prepare_arrays_and_labels(
        dataset_path, suffix,
        lambda array_shape: (reduce(operator.mul, array_shape),),
        lambda array: array.flatten())
