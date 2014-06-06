import os
import sys
import cPickle as pickle
from crosscompute.libraries import script


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--batches_folder', metavar='FOLDER', required=True,
            help='')


def run(
        target_folder, batches_folder):
    batches_path = os.path.join(batches_folder, 'batches.meta')
    value_by_key = pickle.load(open(batches_path))
    print '%s,%s,%s' % value_by_key['array_shape']
