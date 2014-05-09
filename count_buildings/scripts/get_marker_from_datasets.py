import sys
from crosscompute.libraries import script


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        pass


def run(
        target_folder):
    pass
