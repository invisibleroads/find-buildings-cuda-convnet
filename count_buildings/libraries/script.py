import os
import re
import shutil
from argparse import ArgumentParser


def get_argument_parser():
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder',
        metavar='FOLDER',
        required=True)
    return argument_parser


def parse_arguments(argument_parser):
    arguments = argument_parser.parse_args()
    shutil.rmtree(arguments.target_folder, ignore_errors=True)
    os.makedirs(arguments.target_folder)
    return arguments


def parse_dimensions(text):
    return [float(x) for x in re.split(r'[,x]', text)]
