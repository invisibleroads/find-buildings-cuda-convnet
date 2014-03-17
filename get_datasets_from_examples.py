import h5py
import os
import re
import numpy as np
from random import shuffle

from count_buildings.libraries import script


SCALE_BY_UNIT = {
    'h': 10 ** 2,
    'k': 10 ** 3,
    'm': 10 ** 6,
    'g': 10 ** 9,
}


def run(target_folder, example_path, dataset_size, preserve_ratio):
    example_name = os.path.basename(example_path)
    example_h5 = h5py.File(example_path, 'r')
    positive_count = len(example_h5['positive']['pixel_centers'])
    negative_count = len(example_h5['negative']['pixel_centers'])
    example_size = positive_count + negative_count
    dataset_size = min(dataset_size or example_size, example_size)
    if dataset_size == example_size:
        preserve_ratio = True
    dataset_name = get_dataset_name(
        example_name, dataset_size, preserve_ratio)
    dataset_path = os.path.join(target_folder, dataset_name)
    dataset_h5 = h5py.File(dataset_path, 'w')

    if preserve_ratio:
        positive_count *= dataset_size / example_size
    positives = example_h5['positive']['arrays'][:positive_count]
    negative_count = dataset_size - positive_count
    negatives = example_h5['negative']['arrays'][:negative_count]
    arrays = np.row_stack([positives, negatives])
    labels = np.zeros(dataset_size, dtype=bool)
    labels[:positive_count] = True

    indices = range(dataset_size)
    shuffle(indices)
    dataset_h5['arrays'] = arrays[indices]
    dataset_h5['labels'] = labels[indices]


def get_dataset_name(source_path, dataset_size, preserve_ratio):
    source_name = os.path.basename(source_path)
    file_name, file_extension = os.path.splitext(source_name)
    parts = [
        file_name,
        'd%s' % format_dataset_size(dataset_size),
    ]
    if preserve_ratio:
        parts.append('p')
    return '-'.join(parts) + file_extension


def parse_dataset_size(dataset_size_string):
    dataset_size_string = dataset_size_string.lower()
    dataset_size_template = r'(\d+)([%s])' % ''.join(SCALE_BY_UNIT)
    try:
        scaled_size, unit = re.match(
            dataset_size_template, dataset_size_string).groups()
        scale = SCALE_BY_UNIT[unit]
    except AttributeError:
        scaled_size = dataset_size_string
        scale = 1
    scaled_size = int(scaled_size)
    return scaled_size * scale


def format_dataset_size(dataset_size):
    scale_unit_packs = [
        (scale, unit) for unit, scale in SCALE_BY_UNIT.iteritems()]
    for scale, unit in sorted(scale_unit_packs, reverse=True):
        scaled_size = dataset_size / int(scale)
        if scaled_size != dataset_size / float(scale):
            continue
        return '%s%s' % (scaled_size, unit)
    return str(dataset_size)


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        'source_example_path')
    argument_parser.add_argument(
        '--dataset_size', type=parse_dataset_size)
    argument_parser.add_argument(
        '--preserve_ratio', action='store_true')
    arguments = script.parse_arguments(argument_parser)
    run(
        arguments.target_folder,
        arguments.source_example_path,
        arguments.dataset_size,
        arguments.preserve_ratio)
