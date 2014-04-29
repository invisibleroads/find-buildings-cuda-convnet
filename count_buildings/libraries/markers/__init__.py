import cPickle as pickle
import os
from importlib import import_module


class AbstractMarker(object):

    def __init__(self):
        self.variables = {}


def load_marker(folder):
    variables = pickle.load(open(os.path.join(folder, 'run.pkl')))
    marker = initialize_marker(variables['arguments']['marker_module'])
    marker.load(folder)
    return marker


def initialize_marker(marker_module_name):
    marker_module = import_module(__package__ + '.' + marker_module_name)
    return marker_module.Marker()
