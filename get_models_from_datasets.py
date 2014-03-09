import h5py
from count_buildings.libraries import script


def run(target_folder, dataset_path):
    dataset_h5 = h5py.File(dataset_path, 'r')


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        'source_dataset_path')
    arguments = script.parse_arguments(argument_parser)
    run(
        arguments.target_folder,
        arguments.source_dataset_path)
