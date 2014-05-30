import cPickle as pickle
import numpy as np
import os
import sys
from crosscompute.libraries import script
from random import shuffle

from count_buildings.libraries.dataset import DatasetGroup
from count_buildings.libraries.dataset import get_vector_from_array


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--dataset_folders', metavar='FOLDER', required=True, nargs='+',
            help='selections of positive and negative examples')
        starter.add_argument(
            '--batch_size', metavar='SIZE', required=True,
            type=script.parse_size,
            help='maximum number of examples to include per batch')


def run(
        target_folder, dataset_folders, batch_size):
    dataset_group = DatasetGroup(dataset_folders)
    keys = dataset_group.get_keys()
    shuffle(keys)
    save_meta(target_folder, dataset_group, keys)
    save_data(target_folder, dataset_group, keys, batch_size)


def save_meta(target_folder, dataset_group, keys):
    target_path = os.path.join(target_folder, 'batches.meta')
    array_mean = dataset_group.array_mean
    array_sd = dataset_group.array_sd

    vector_mean = get_vector_from_array(array_mean)
    vector_sd = get_vector_from_array(array_sd)
    vector_size = vector_mean.size

    transform_vector = lambda x: x.reshape(vector_size, 1).astype(np.single)
    pickle.dump({
        'data_mean': transform_vector(vector_mean),
        'data_sd': transform_vector(vector_sd),
        'label_names': ['', 'building'],
        'num_vis': vector_size,
        'packs': map(tuple, dataset_group.get_pixel_centers(keys)),
        'pack_columns': ['pixel_center_x', 'pixel_center_y'],
        'array_shape': array_mean.shape,
    }, open(target_path, 'w'), protocol=-1)


def save_data(target_folder, dataset_group, keys, batch_size):
    target_path_template = os.path.join(target_folder, 'data_batch_%d')
    start_indices = xrange(0, len(keys), batch_size)
    for batch_index, start_index in enumerate(start_indices):
        selected_keys = keys[start_index:start_index + batch_size]

        data = dataset_group.get_data(selected_keys)
        labels = dataset_group.get_labels(selected_keys)

        pickle.dump({
            'ids': range(start_index, start_index + len(selected_keys)),
            'data': data.astype(np.single),
            'labels': [1 if x else 0 for x in labels],
        }, open(target_path_template % batch_index, 'w'), protocol=-1)
