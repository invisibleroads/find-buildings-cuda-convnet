import h5py
import os
import random
import sys
from crosscompute.libraries import script
from shapely.geometry import box

from ..libraries import satellite_image
from ..libraries.dataset import DATASET_NAME
from .get_examples_from_points import EXAMPLES_NAME


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--examples_folder', metavar='FOLDER', required=True,
            help='extracted examples')
        starter.add_argument(
            '--maximum_dataset_size', metavar='SIZE',
            type=script.parse_size,
            help='maximum number of examples to include')
        starter.add_argument(
            '--preserve_ratio', action='store_true',
            help='preserve ratio of positive to negative examples')
        starter.add_argument(
            '--excluded_pixel_bounds', metavar='MIN_X,MIN_Y,MAX_X,MAX_Y',
            type=script.parse_bounds,
            help='ignore specified bounds')
        starter.add_argument(
            '--batch_size', metavar='SIZE',
            type=script.parse_size,
            help='ensure dataset size is divisible by batch size')


def run(
        target_folder, examples_folder, maximum_dataset_size,
        preserve_ratio, excluded_pixel_bounds, batch_size):
    examples_h5 = h5py.File(os.path.join(examples_folder, EXAMPLES_NAME), 'r')
    positive_indices = get_indices(
        examples_h5['positive'], maximum_dataset_size, excluded_pixel_bounds)
    negative_indices = get_indices(
        examples_h5['negative'], maximum_dataset_size, excluded_pixel_bounds)
    positive_count, negative_count = adjust_counts(
        len(positive_indices), len(negative_indices),
        maximum_dataset_size, preserve_ratio, batch_size)
    dataset_h5 = get_dataset_h5(target_folder)
    save_dataset(
        dataset_h5, examples_h5,
        positive_indices[:positive_count],
        negative_indices[:negative_count])
    return dict(
        dataset_size=script.format_size(positive_count + negative_count),
        positive_count=positive_count,
        negative_count=negative_count)


def get_indices(examples, maximum_dataset_size, excluded_pixel_bounds):
    pixel_centers = examples['pixel_centers'][:maximum_dataset_size]
    pixel_dimensions = examples['arrays'].shape[1:3]
    if not excluded_pixel_bounds:
        return range(len(pixel_centers))
    indices = []
    excluded_pixel_box = box(*excluded_pixel_bounds)
    for index, pixel_center in enumerate(pixel_centers):
        pixel_bounds = satellite_image.get_pixel_bounds_from_pixel_center(
            pixel_center, pixel_dimensions)
        pixel_box = box(*pixel_bounds)
        if pixel_box.intersects(excluded_pixel_box):
            continue
        indices.append(index)
    return indices


def adjust_counts(
        positive_count, negative_count,
        maximum_dataset_size, preserve_ratio, batch_size):
    example_count = positive_count + negative_count
    dataset_size = min(maximum_dataset_size or example_count, example_count)
    if batch_size:
        dataset_size = (dataset_size / batch_size) * batch_size
    if dataset_size == example_count:
        preserve_ratio = True
    if preserve_ratio:
        positive_ratio = positive_count / float(example_count)
        positive_count = int(positive_ratio * dataset_size)
    negative_count = dataset_size - positive_count
    return positive_count, negative_count


def get_dataset_h5(target_folder):
    return h5py.File(os.path.join(target_folder, DATASET_NAME), 'w')


def save_dataset(dataset_h5, examples_h5, positive_indices, negative_indices):
    dataset_size = len(positive_indices) + len(negative_indices)
    positive_packs = [(_, True) for _ in positive_indices]
    negative_packs = [(_, False) for _ in negative_indices]
    dataset_packs = positive_packs + negative_packs
    random.shuffle(dataset_packs)
    positive_arrays = examples_h5['positive']['arrays']
    positive_pixel_centers = examples_h5['positive']['pixel_centers']
    arrays = dataset_h5.create_dataset(
        'arrays', shape=(dataset_size,) + positive_arrays.shape[1:],
        dtype=positive_arrays.dtype)
    pixel_centers = dataset_h5.create_dataset(
        'pixel_centers', shape=(dataset_size, 2),
        dtype=positive_pixel_centers.dtype)
    for key, value in positive_pixel_centers.attrs.iteritems():
        pixel_centers.attrs[key] = value
    labels = dataset_h5.create_dataset(
        'labels', shape=(dataset_size,), dtype=bool)
    for index, (inner_index, label) in enumerate(dataset_packs):
        inner_examples = examples_h5['positive' if label else 'negative']
        arrays[index, :, :, :] = inner_examples['arrays'][inner_index]
        labels[index] = label
        pixel_centers[index, :] = inner_examples['pixel_centers'][inner_index]
