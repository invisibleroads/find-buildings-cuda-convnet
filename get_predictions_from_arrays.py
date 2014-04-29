import h5py
import os
from osgeo import ogr

from count_buildings.libraries import satellite_image
from count_buildings.libraries import script
from count_buildings.libraries.markers import load_marker
from geometryIO import save_points


def run(target_folder, arrays_path, marker_folder):
    marker = load_marker(marker_folder)
    predictions = marker.scan(arrays_path)
    pixel_centers = get_pixel_centers(arrays_path, predictions)
    save_predictions_h5(
        target_folder, predictions, pixel_centers, arrays_path)
    save_predictions_shapefile(
        target_folder, predictions, pixel_centers, arrays_path)
    return dict(
        positive_count=len(pixel_centers))


def get_pixel_centers(arrays_path, predictions):
    arrays_h5 = h5py.File(arrays_path, 'r')
    arrays = arrays_h5['arrays']
    pixel_upper_lefts = arrays_h5['pixel_upper_lefts']
    pixel_centers = []
    for index, prediction in enumerate(predictions):
        if not prediction:
            continue
        pixel_centers.append(satellite_image.get_pixel_center_from_pixel_frame(
            (pixel_upper_lefts[index], get_pixel_dimensions(arrays[index]))))
    return pixel_centers


def get_pixel_dimensions(array):
    pixel_height, pixel_width = array.shape[:2]
    return pixel_width, pixel_height


def save_predictions_h5(
        target_folder, predictions, pixel_centers, arrays_path):
    arrays_h5 = h5py.File(arrays_path, 'r')
    pixel_upper_lefts = arrays_h5['pixel_upper_lefts']
    pixel_dtype = pixel_upper_lefts.dtype
    # Save
    predictions_h5 = h5py.File(
        os.path.join(target_folder, 'predictions.h5'), 'w')
    predictions = predictions_h5.create_dataset(
        'predictions', data=predictions, dtype=bool)
    pixel_centers = predictions_h5.create_dataset(
        'pixel_centers', data=pixel_centers, dtype=pixel_dtype)
    for key, value in pixel_upper_lefts.attrs.iteritems():
        pixel_centers.attrs[key] = value


def save_predictions_shapefile(
        target_folder, predictions, pixel_centers, arrays_path):
    arrays_h5 = h5py.File(arrays_path, 'r')
    pixel_upper_lefts = arrays_h5['pixel_upper_lefts']
    calibration_pack = pixel_upper_lefts.attrs['calibration_pack']
    proj4 = pixel_upper_lefts.attrs['proj4']
    # Convert pixel coordinates to spatial coordinates
    calibration = satellite_image.Calibration(calibration_pack)
    centers = [calibration.to_xy(_) for _ in pixel_centers]
    field_packs = [(_,) for _ in predictions]
    field_definitions = [('Prediction', ogr.OFTReal)]
    # Save
    save_points(
        os.path.join(target_folder, 'predictions.shp'), proj4, centers,
        field_packs, field_definitions)


if __name__ == '__main__':
    argument_parser = script.get_argument_parser()
    argument_parser.add_argument(
        '--arrays_path', metavar='PATH',
        required=True)
    argument_parser.add_argument(
        '--marker_folder', metavar='FOLDER',
        required=True)
    arguments = script.parse_arguments(argument_parser)
    variables = run(**arguments.__dict__)
    script.save_run(arguments, variables, verbose=True)
