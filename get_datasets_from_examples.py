import h5py
import os
from random import shuffle
from shapely.geometry import box

from count_buildings.libraries import disk
from count_buildings.libraries import script
from count_buildings.libraries import satellite_image


def run(
        target_folder, example_path,
        dataset_size, preserve_ratio, stay_outside_pixel_bounds):
    example_h5 = h5py.File(example_path, 'r')
    positive_indices = get_indices(
        example_h5['positive'], dataset_size, stay_outside_pixel_bounds)
    negative_indices = get_indices(
        example_h5['negative'], dataset_size, stay_outside_pixel_bounds)
    target_positive_count, target_negative_count = adjust_counts(
        len(positive_indices),
        len(negative_indices), dataset_size, preserve_ratio)
    target_dataset_size = target_positive_count + target_negative_count
    dataset_h5 = get_dataset_h5(
        target_folder, example_path, target_dataset_size, preserve_ratio)
    save_dataset(
        dataset_h5, example_h5,
        positive_indices[:target_positive_count],
        negative_indices[:target_negative_count])
    return dict(
        dataset_size=script.format_size(target_dataset_size),
        positive_count=target_positive_count,
        negative_count=target_negative_count)


def get_indices(examples, dataset_size, excluded_pixel_bounds):
    indices = []
    pixel_centers = examples['pixel_centers'][:dataset_size]
    example_pixel_dimensions = examples['arrays'].shape[1:3]
    excluded_pixel_box = box(
        *excluded_pixel_bounds) if excluded_pixel_bounds else None
    for index, pixel_center in enumerate(pixel_centers):
        if excluded_pixel_box:
            pixel_bounds = satellite_image.get_pixel_bounds_from_pixel_center(
                pixel_center, example_pixel_dimensions)
            pixel_box = box(*pixel_bounds)
            if pixel_box.intersects(excluded_pixel_box):
                continue
        indices.append(index)
    return indices


def adjust_counts(
        positive_count, negative_count, dataset_size, preserve_ratio):
    example_size = positive_count + negative_count
    dataset_size = min(dataset_size or example_size, example_size)
    if dataset_size == example_size:
        preserve_ratio = True
    if preserve_ratio:
        positive_ratio = positive_count / float(example_size)
        positive_count = int(positive_ratio * dataset_size)
    negative_count = dataset_size - positive_count
    return positive_count, negative_count


def save_dataset(dataset_h5, example_h5, positive_indices, negative_indices):
    positive_count = len(positive_indices)
    negative_count = len(negative_indices)
    dataset_size = positive_count + negative_count

    positive_packs = [(_, True) for _ in positive_indices]
    negative_packs = [(_, False) for _ in negative_indices]
    dataset_packs = positive_packs + negative_packs
    shuffle(dataset_packs)

    array_shape = example_h5['positive']['arrays'].shape[1:]
    array_dtype = example_h5['positive']['arrays'].dtype
    arrays = dataset_h5.create_dataset(
        'arrays', shape=(dataset_size,) + array_shape, dtype=array_dtype)
    labels = dataset_h5.create_dataset(
        'labels', shape=(dataset_size,), dtype=bool)
    pixel_center_dtype = example_h5['positive']['pixel_centers'].dtype
    pixel_centers = dataset_h5.create_dataset(
        'pixel_centers', shape=(dataset_size, 2), dtype=pixel_center_dtype)
    for index, (inner_index, label) in enumerate(dataset_packs):
        inner_key = 'positive' if label else 'negative'
        inner_examples = example_h5[inner_key]

        arrays[index, :, :, :] = inner_examples['arrays'][inner_index]
        labels[index] = label
        pixel_centers[index, :] = inner_examples['pixel_centers'][inner_index]


def get_dataset_h5(target_folder, source_path, dataset_size, preserve_ratio):
    parts = [
        disk.get_basename(source_path),
        'd%s' % script.format_size(dataset_size)]
    if preserve_ratio:
        parts.append('p')
    dataset_name = '-'.join(parts) + '.h5'
    dataset_path = os.path.join(target_folder, dataset_name)
    return h5py.File(dataset_path, 'w')


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        '--example_path', metavar='PATH', required=True,
        help='extracted examples')
    argument_parser.add_argument(
        '--dataset_size', metavar='INTEGER',
        type=script.parse_size,
        help='maximum number of examples to include')
    argument_parser.add_argument(
        '--preserve_ratio', action='store_true',
        help='preserve ratio of positive to negative examples')
    argument_parser.add_argument(
        '--stay_outside_pixel_bounds', metavar='MIN_X,MIN_Y,MAX_X,MAX_Y',
        type=script.parse_bounds,
        help='ignore specified bounds')
    arguments = script.parse_arguments(argument_parser)
    variables = run(**arguments.__dict__)
    script.save_run(arguments, variables, verbose=True)
