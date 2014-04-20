from importlib import import_module

from count_buildings.libraries import script


MARKERS_FOLDER = 'count_buildings.libraries.markers'


def run(target_folder, dataset_path, marker_module, cross_validate_only):
    marker = get_marker(marker_module)
    if cross_validate_only:
        return marker.cross_validate(dataset_path)
    marker.calibrate(dataset_path)
    return marker.save(target_folder)


def get_marker(marker_module):
    marker_module = import_module(MARKERS_FOLDER + '.' + marker_module)
    return marker_module.Marker()


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        '--dataset_path', metavar='PATH',
        required=True,
        help='')
    # argument_parser.add_argument(
        # '--transformations', metavar='NAMES',
        # help='')
    argument_parser.add_argument(
        '--marker_module', metavar='PACKAGE',
        required=True,
        help='')
    argument_parser.add_argument(
        '--cross_validate_only', action='store_true',
        help='')
    arguments = script.parse_arguments(argument_parser)
    variables = run(**arguments.__dict__)
    script.save_run(arguments, variables, verbose=True)
