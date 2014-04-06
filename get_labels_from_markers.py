import datetime
import h5py
import os
from sklearn.externals import joblib
from sklearn.linear_model import LinearRegression

from count_buildings.libraries import disk
from count_buildings.libraries import script


class Marker(object):

    def calibrate(self, arrays, labels):
        processed_arrays = [_.flatten() for _ in arrays]
        self.model = LinearRegression()
        self.model.fit(processed_arrays, labels)

    def save(self, target_folder):
        target_path = os.path.join(target_folder, 'joblib')
        joblib.dump(self.model, target_path)


def run(target_folder, dataset_path):
    dataset_h5 = h5py.File(dataset_path, 'r')
    dataset_arrays = dataset_h5['arrays']
    dataset_labels = dataset_h5['labels']
    marker_name = get_marker_name(dataset_path)
    target_marker_folder = disk.replace_folder(target_folder, marker_name)

    marker = Marker()
    marker.calibrate(dataset_arrays, dataset_labels)
    marker.save(target_marker_folder)


def get_marker_name(dataset_path):
    parts = [
        disk.get_basename(dataset_path),
        datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
    ]
    return '-'.join(parts)


if __name__ == '__main__':
    argument_parser.add_argument(
        'source_dataset_path')
    arguments = script.parse_arguments(argument_parser)
    run(
        arguments.target_folder,
        arguments.source_dataset_path)


'source_marker_path'
'source_image_path'

python get_labels_from_markers.py


    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        'source_marker_path')
    argument_parser.add_argument(
        'source_image_path')


    argument_parser.add_argument(
        '--tile_indices',
        metavar='0,1,2',
        type=script.parse_numbers,
        help='indices to scan')
    argument_parser.add_argument(
        '--tile_dimensions',
        metavar='WIDTH,HEIGHT',
        required=True,
        type=script.parse_dimensions,
        help='dimensions of extracted tile in geographic units')
    argument_parser.add_argument(
        '--interval_dimensions',
        metavar='WIDTH,HEIGHT',
        required=True,
        type=script.parse_dimensions,
        help='dimensions of scanning interval in geographic units')
    arguments = script.parse_arguments(argument_parser)
    run(
        arguments.target_folder,
        arguments.source_image_path,
        arguments.tile_indices,
        arguments.tile_dimensions,
        arguments.interval_dimensions)
