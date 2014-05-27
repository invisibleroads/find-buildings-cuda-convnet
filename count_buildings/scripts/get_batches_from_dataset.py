import cPickle as pickle
import h5py
import numpy as np
import os
import sys
from crosscompute.libraries import script

from .get_dataset_from_examples import DATASET_NAME


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--dataset_folder', metavar='FOLDER', required=True,
            help='selection of positive and negative examples')
        starter.add_argument(
            '--batch_size', metavar='SIZE', required=True,
            type=script.parse_size,
            help='maximum number of examples to include per batch')


def run(
        target_folder, dataset_folder, batch_size):
    dataset_h5 = h5py.File(os.path.join(dataset_folder, DATASET_NAME))
    arrays = dataset_h5['arrays'].value
    array_shape = arrays.shape[1:]

    vectors = arrays.swapaxes(1, 3).swapaxes(2, 3).reshape((
        arrays.shape[0], -1))
    labels = dataset_h5['labels']
    label_names = ['', 'building']
    pixel_centers = dataset_h5['pixel_centers']

    save_meta(target_folder, vectors, label_names, pixel_centers, array_shape)
    save_data(target_folder, vectors, labels, batch_size)


def save_meta(target_folder, vectors, label_names, pixel_centers, array_shape):
    # Prepare
    target_path = os.path.join(target_folder, 'batches.meta')
    vector_mean = vectors.mean(axis=0)
    vector_size = vector_mean.size
    # Save
    pickle.dump({
        'data_mean': vector_mean.reshape(vector_size, 1).astype(np.single),
        'label_names': ['', 'building'],
        'num_vis': vector_size,
        'packs': map(tuple, pixel_centers),
        'pack_columns': ['pixel_center_x', 'pixel_center_y'],
        'array_shape': array_shape,
    }, open(target_path, 'w'), protocol=-1)


def save_data(target_folder, vectors, labels, batch_size):
    target_path_template = os.path.join(target_folder, 'data_batch_%d')
    start_indices = xrange(0, len(vectors), batch_size)
    for batch_index, start_index in enumerate(start_indices):
        end_index = start_index + batch_size
        # Prepare
        target_path = target_path_template % batch_index
        data = vectors[start_index:end_index].T
        array_count = data.shape[1]
        # Save
        pickle.dump({
            'ids': range(start_index, start_index + array_count),
            'data': data.astype(np.single),
            'labels': [1 if x else 0 for x in labels[start_index:end_index]],
        }, open(target_path, 'w'), protocol=-1)
