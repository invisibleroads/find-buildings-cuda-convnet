import re
import sys
from glob import glob


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--batches_folder', metavar='FOLDER', required=True,
            help='')


def run(
        target_folder, batches_folder):
    pattern_number = re.compile(r'\d+')
    max_index = 0
    for name in glob(os.path.join(batches_folder, 'data_batch_*')):
        index = int(pattern_number.search(name).group(1))
        if index > max_index:
            max_index = index
    print max_index
