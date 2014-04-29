from count_buildings.libraries import script
from count_buildings.libraries.markers import initialize_marker


def run(target_folder, dataset_path, marker_module, cross_validate_only):
    marker = initialize_marker(marker_module)
    if cross_validate_only:
        return marker.cross_validate(dataset_path)
    marker.calibrate(dataset_path)
    return marker.save(target_folder)


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
