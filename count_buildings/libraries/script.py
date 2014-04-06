import cPickle as pickle
import numpy as np
import os
import re
from argparse import ArgumentParser

from count_buildings.libraries import disk


SCALE_BY_UNIT = {
    'h': 10 ** 2,
    'k': 10 ** 3,
    'm': 10 ** 6,
    'g': 10 ** 9,
}


def get_argument_parser():
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        '--target_folder', metavar='FOLDER', required=True,
        type=disk.normalize_path,
        help='output folder')
    return argument_parser


def parse_arguments(argument_parser):
    arguments = argument_parser.parse_args()
    disk.make_folder(arguments.target_folder)
    return arguments


def parse_bounds(text):
    x1, y1, x2, y2 = parse_numbers(text)
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


def parse_dimensions(text):
    return np.array([float(x) for x in re.split(r'[,x]', text)])


def parse_numbers(text):
    return [int(x) for x in text.split(',')]


def parse_size(text):
    text = text.lower()
    size_template = r'(\d+)([%s])' % ''.join(SCALE_BY_UNIT)
    try:
        scaled_size, unit = re.match(size_template, text).groups()
        scale = SCALE_BY_UNIT[unit]
    except AttributeError:
        scaled_size = text
        scale = 1
    scaled_size = int(scaled_size)
    return scaled_size * scale


def format_size(size):
    scale_unit_packs = [
        (scale, unit) for unit, scale in SCALE_BY_UNIT.iteritems()]
    for scale, unit in sorted(scale_unit_packs, reverse=True):
        scaled_size = size / int(scale)
        if scaled_size != size / float(scale):
            continue
        return '%s%s' % (scaled_size, unit)
    return str(size)


def save_run(arguments, variables, verbose=False):
    value_by_key = dict(arguments=arguments.__dict__, variables=variables)
    target_path = os.path.join(arguments.target_folder, 'run.pkl')
    target_file = open(target_path, 'wb')
    pickle.dump(value_by_key, target_file, protocol=-1)
    verbose and show_variables(variables)
    return value_by_key


def show_variables(variables):
    for item in variables.iteritems():
        print('%s = %s' % item)
