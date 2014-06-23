import cPickle as pickle
import numpy as np
import os
import sys
from crosscompute.libraries import script

from .get_dataset_from_examples import DATASET_NAME
from ..libraries.dataset import BatchGroup
from ..libraries.dataset import get_vector_from_array


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--dataset_folders', metavar='FOLDER', required=True,
            nargs='+',
            help='selections of positive and negative examples')
        starter.add_argument(
            '--batch_size', metavar='SIZE', required=True,
            type=script.parse_size,
            help='maximum number of examples to include per batch')
        starter.add_argument(
            '--array_shape', metavar='HEIGHT,WIDTH,BAND_COUNT',
            type=script.parse_numbers,
            help='')


def run(
        target_folder, dataset_folders, batch_size, array_shape):
    batch_group = BatchGroup(
        DATASET_NAME, dataset_folders, batch_size, array_shape)
    keys = batch_group.keys
    save_meta(target_folder, batch_group, keys)
    batch_count = save_data(target_folder, batch_group, keys, batch_size)
    return dict(
        array_count=batch_group.array_count,
        array_shape=batch_group.array_shape,
        batch_count=batch_count,
        positive_count=sum(batch_group.get_labels(keys)))


def save_meta(target_folder, batch_group, keys):
    target_path = os.path.join(target_folder, 'batches.meta')
    array_mean = batch_group.array_mean

    vector_mean = get_vector_from_array(array_mean)
    vector_size = vector_mean.size

    transform_vector = lambda x: x.reshape(vector_size, 1).astype(np.single)
    pickle.dump({
        'data_mean': transform_vector(vector_mean),
        'label_names': ['', 'building'],
        'num_vis': vector_size,
        'packs': map(tuple, batch_group.get_pixel_centers(keys)),
        'pack_columns': ['pixel_center_x', 'pixel_center_y'],
        'array_shape': array_mean.shape,
    }, open(target_path, 'w'), protocol=-1)


def save_data(target_folder, batch_group, keys, batch_size):
    target_path_template = os.path.join(target_folder, 'data_batch_%d')
    start_indices = xrange(0, len(keys), batch_size)
    batch_index = 0
    batch_count = len(start_indices)
    for batch_index, start_index in enumerate(start_indices):
        if batch_index % 10 == 0:
            print '%s / %s' % (batch_index, batch_count - 1)
        selected_keys = keys[start_index:start_index + batch_size]
        data = batch_group.get_data(selected_keys)
        labels = batch_group.get_labels(selected_keys)
        pickle.dump({
            'ids': range(start_index, start_index + len(selected_keys)),
            'data': data.astype(np.single),
            'labels': [1 if x else 0 for x in labels],
        }, open(target_path_template % batch_index, 'w'), protocol=-1)
    print '%s / %s' % (batch_index, batch_count - 1)
    return batch_count
