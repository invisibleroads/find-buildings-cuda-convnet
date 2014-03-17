import re
from argparse import ArgumentParser

from count_buildings.libraries import disk


def get_argument_parser():
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
        metavar='FOLDER',
        required=True)
    return argument_parser


def parse_arguments(argument_parser):
    arguments = argument_parser.parse_args()
    disk.make_folder(arguments.target_folder)
    return arguments


def parse_numbers(text):
    return [int(x) for x in text.split(',')]


def parse_dimensions(text):
    return [float(x) for x in re.split(r'[,x]', text)]
