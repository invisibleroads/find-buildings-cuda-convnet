import logging
import numpy as np
import sys
from collections import OrderedDict
from crosscompute.libraries import script
from geometryIO import GeometryError, load_points

from ..libraries.satellite_image import SatelliteImage
from ..libraries.kdtree import KDTree


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='satellite image')
        starter.add_argument(
            '--points_path', metavar='PATH', required=True,
            help='')
        starter.add_argument(
            '--counts_path', metavar='PATH', required=True,
            help='')
        starter.add_argument(
            '--maximum_metric_radius', metavar='METERS', required=True,
            type=float,
            help='')


def run(
        target_folder, image_path, points_path, counts_path,
        maximum_metric_radius):
    image = SatelliteImage(image_path)
    assert '+units=m' in image.proj4
    try:
        old_locations = load_points(points_path, targetProj4=image.proj4)[1]
    except GeometryError:
        logging.warn('could not load points_path=%s' % points_path)
        old_locations = []
    try:
        new_locations = load_points(counts_path, targetProj4=image.proj4)[1]
    except GeometryError:
        logging.warn('could not load counts_path=%s' % counts_path)
        new_locations = []

    old_locations = select_projected_xys(old_locations, image)
    new_locations = select_projected_xys(new_locations, image)

    old_location_count = len(old_locations)
    new_location_count = len(new_locations)

    if old_location_count == 0 or new_location_count == 0:
        old_indices = []
    else:
        old_indices = KDTree(old_locations).query(
            new_locations, maximum_distance=maximum_metric_radius)[1]

    true_positive_count = len(set(old_indices))
    false_positive_count = new_location_count - true_positive_count
    false_negative_count = old_location_count - true_positive_count

    try:
        precision = true_positive_count / float(new_location_count)
    except ZeroDivisionError:
        precision = np.inf
    try:
        recall = true_positive_count / float(old_location_count)
    except ZeroDivisionError:
        recall = np.inf
    return OrderedDict([
        ('actual_count', old_location_count),
        ('estimated_count', new_location_count),
        ('true_positive_count', true_positive_count),
        ('false_positive_count', false_positive_count),
        ('false_negative_count', false_negative_count),
        ('precision', precision),
        ('recall', recall),
    ])


def select_projected_xys(projected_xys, image):
    # Define upper left and lower right pixel corners
    pixel_xy1 = 0, 0
    pixel_xy2 = image.pixel_dimensions
    # Convert pixel corners into projected corners
    x1, y1 = image.to_projected_xy(pixel_xy1)
    x2, y2 = image.to_projected_xy(pixel_xy2)
    # Sort coordinates into bounds
    x1, x2 = sorted([x1, x2])
    y1, y2 = sorted([y1, y2])
    # Define filter
    in_image = lambda (x, y): (
        x1 <= x) and (x <= x2) and (
        y1 <= y) and (y <= y2)
    # Apply filter
    return filter(in_image, projected_xys)
