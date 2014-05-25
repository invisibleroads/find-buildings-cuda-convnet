import cPickle as pickle
import h5py
import numpy as np
import os
import sys
from crosscompute.libraries import script
from operator import mul

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
    dataset_path = os.path.join(dataset_folder, DATASET_NAME)
    dataset_h5 = h5py.File(dataset_path)
    print 1
    arrays = dataset_h5['arrays'].value
    vectors = arrays.swapaxes(1, 3).reshape((
        arrays.shape[0], reduce(mul, arrays.shape[1:])))
    labels = dataset_h5['labels']
    label_names = ['', 'building']
    pixel_centers = dataset_h5['pixel_centers']
    print 2
    save_meta(target_folder, vectors, label_names, pixel_centers)
    save_data(target_folder, vectors, labels, batch_size)


def save_meta(target_folder, vectors, label_names, pixel_centers):
    print 'meta 0'
    # Prepare
    target_path = os.path.join(target_folder, 'batches.meta')
    print 'meta mean'
    vector_mean = vectors.mean(axis=0)
    vector_size = vector_mean.size
    print 'meta dump'
    # Save
    pickle.dump({
        'data_mean': vector_mean.reshape(vector_size, 1).astype(np.single),
        'label_names': ['', 'building'],
        'num_vis': vector_size,
        'packs': map(tuple, pixel_centers),
        'pack_columns': ['pixel_center_x', 'pixel_center_y'],
    }, open(target_path, 'w'), protocol=-1)


def save_data(target_folder, vectors, labels, batch_size):
    target_path_template = os.path.join(target_folder, 'data_batch_%d')
    start_indices = xrange(0, len(vectors), batch_size)
    for batch_index, start_index in enumerate(start_indices):
        print 'batch %s' % batch_index
        end_index = start_index + batch_size
        # Prepare
        target_path = target_path_template % batch_index
        data = vectors[start_index:end_index].T
        print 'batch %s dump' % batch_index
        # Save
        pickle.dump({
            'ids': range(len(vectors)),
            'data': data.astype(np.single),
            'labels': [1 if x else 0 for x in labels[start_index:end_index]],
        }, open(target_path, 'w'), protocol=-1)
