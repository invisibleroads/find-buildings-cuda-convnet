import geometryIO
import numpy as np
import os
import sys
from count_buildings.libraries.kdtree import KDTree
from count_buildings.libraries.satellite_image import SatelliteImage
from crosscompute.libraries import script
from geometryIO import get_transformPoint
from pandas import read_csv


COUNTS_SHP = 'counts.shp'
PROBABILITIES_CSV = 'probabilities.csv'
PROBABILITIES_SHP = 'probabilities.shp'


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--probabilities_folder', metavar='FOLDER', required=True,
            help='')
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='satellite image')
        starter.add_argument(
            '--points_path', metavar='PATH',
            help='')
        starter.add_argument(
            '--actual_count', metavar='INTEGER',
            type=int,
            help='')
        starter.add_argument(
            '--actual_metric_radius', metavar='METERS',
            type=float,
            help='')
        starter.add_argument(
            '--minimum_metric_radius', metavar='METERS',
            type=float,
            help='')
        starter.add_argument(
            '--maximum_metric_radius', metavar='METERS',
            type=float,
            help='')


def run(
        target_folder, probabilities_folder,
        image_path, points_path, actual_count, actual_metric_radius,
        minimum_metric_radius, maximum_metric_radius):
    value_by_key = {}
    probability_packs = get_probability_packs(probabilities_folder)
    image = SatelliteImage(image_path)
    if not points_path and not actual_count and not actual_metric_radius:
        pixel_centers = probability_packs[[
            'pixel_center_x', 'pixel_center_y']].values
        target_path = os.path.join(target_folder, PROBABILITIES_SHP)
        save_pixel_centers(target_path, pixel_centers, image)
        return dict(probability_count=len(pixel_centers))
    elif points_path:
        pixel_bounds = get_pixel_bounds(probabilities_folder)
        actual_count = get_actual_count(image, points_path, pixel_bounds)
        value_by_key['pixel_bounds'] = pixel_bounds

    to_pixel_radius = lambda metric_radius: min(image.to_pixel_dimensions((
        metric_radius, metric_radius)))
    to_metric_radius = lambda pixel_radius: min(image.to_metric_dimensions((
        pixel_radius, pixel_radius)))

    if actual_metric_radius is not None:
        selected_pixel_radius = to_pixel_radius(actual_metric_radius)
        selected_pixel_centers = get_selected_pixel_centers(
            probability_packs, selected_pixel_radius)
        value_by_key['selected_metric_radius'] = to_metric_radius(
            selected_pixel_radius)
    elif actual_count is not None:
        minimum_pixel_radius = to_pixel_radius(
            minimum_metric_radius) if minimum_metric_radius else 1
        maximum_pixel_radius = to_pixel_radius(
            maximum_metric_radius) if maximum_metric_radius else np.inf
        best_pixel_radiuses, selected_pixel_centers = determine_pixel_radius(
            probability_packs, actual_count,
            minimum_pixel_radius, maximum_pixel_radius)
        value_by_key['minimum_best_metric_radius'] = to_metric_radius(
            min(best_pixel_radiuses))
        value_by_key['maximum_best_metric_radius'] = to_metric_radius(
            max(best_pixel_radiuses))
    target_path = os.path.join(target_folder, COUNTS_SHP)
    save_pixel_centers(target_path, selected_pixel_centers, image)
    estimated_count = len(selected_pixel_centers)

    if actual_count is not None:
        value_by_key['percent_error'] = 100 * (
            estimated_count - actual_count
        ) / float(actual_count) if actual_count else np.inf
        value_by_key['actual_count'] = actual_count
    return dict(
        probability_count=len(probability_packs),
        estimated_count=estimated_count,
        **value_by_key)


def get_probability_packs(probabilities_folder):
    probabilities_path = os.path.join(probabilities_folder, PROBABILITIES_CSV)
    probabilities_table = read_csv(probabilities_path)
    predictions = probabilities_table[
        probabilities_table['1'] > probabilities_table['0']]
    return predictions[['1', 'pixel_center_x', 'pixel_center_y']]


def get_pixel_bounds(probabilities_folder):
    probabilities_path = os.path.join(probabilities_folder, PROBABILITIES_CSV)
    probabilities_table = read_csv(probabilities_path)
    xys = probabilities_table[['pixel_center_x', 'pixel_center_y']]
    return [
        min(xys.pixel_center_x), min(xys.pixel_center_y),
        max(xys.pixel_center_x), max(xys.pixel_center_y)]


def get_actual_count(image, points_path, pixel_bounds):
    points_proj4, xys = geometryIO.load_points(points_path)[:2]
    transform_point = get_transformPoint(points_proj4, image.proj4)
    pixel_xys = [image.to_pixel_xy(transform_point(*_)) for _ in xys]
    min_pixel_x, min_pixel_y, max_pixel_x, max_pixel_y = pixel_bounds
    included_pixel_xys = set()
    for pixel_x, pixel_y in pixel_xys:
        in_x = min_pixel_x <= pixel_x and pixel_x <= max_pixel_x
        in_y = min_pixel_y <= pixel_y and pixel_y <= max_pixel_y
        if not in_x or not in_y:
            continue
        included_pixel_xys.add((pixel_x, pixel_y))
    return len(included_pixel_xys)


def save_pixel_centers(target_path, pixel_centers, image):
    projected_centers = [image.to_projected_xy(_) for _ in pixel_centers]
    if not projected_centers:
        return
    geometryIO.save_points(target_path, image.proj4, projected_centers)


def determine_pixel_radius(
        probability_packs, actual_count,
        minimum_pixel_radius, maximum_pixel_radius):
    best_margin = np.inf
    best_pixel_centers = []
    best_pixel_radiuses = []
    pixel_radius = minimum_pixel_radius
    while True:
        selected_pixel_centers = get_selected_pixel_centers(
            probability_packs, pixel_radius)
        actual_margin = len(selected_pixel_centers) - actual_count
        print 'pixel_radius >= %s\tactual_margin = %s' % (
            pixel_radius, actual_margin)
        if abs(best_margin) < abs(actual_margin):
            break
        if best_margin != actual_margin:
            best_pixel_radiuses = []
        best_margin = actual_margin
        best_pixel_centers = selected_pixel_centers
        best_pixel_radiuses.append(pixel_radius)
        if pixel_radius >= maximum_pixel_radius:
            break
        if len(selected_pixel_centers) <= 1:
            break
        pixel_radius += 1
    return best_pixel_radiuses, best_pixel_centers


def get_selected_pixel_centers(probability_packs, actual_metric_radius):
    xys = probability_packs[['pixel_center_x', 'pixel_center_y']].values
    return list(yield_hotspot_via_metric(
        xys, radius=actual_metric_radius,
        get_metric=lambda index: probability_packs['1'].values[index]))


def yield_hotspot_via_metric(xys, radius, get_metric):
    pending_indices = np.arange(len(xys))
    while len(pending_indices):
        pending_xys = xys[pending_indices]
        pending_tree = KDTree(pending_xys)
        best_metric, best_hotspot_xy, best_indices = -np.inf, None, []
        for pending_index in pending_indices:
            # Get metric
            metric = get_metric(pending_index)
            if metric < best_metric:
                continue
            xy = xys[pending_index]
            # Get events within radius
            selected_distances, selected_indices = pending_tree.query(
                xy, maximum_distance=radius)
            selected_xys = pending_xys[selected_indices]
            selected_metrics = [
                get_metric(x) for x in pending_indices[selected_indices]]
            # Save
            best_metric = metric
            best_hotspot_xy = np.average(
                selected_xys, axis=0, weights=selected_metrics)
            best_indices = pending_indices[selected_indices]
        yield best_hotspot_xy
        pending_indices = np.array(list(
            set(pending_indices) - set(best_indices)))
