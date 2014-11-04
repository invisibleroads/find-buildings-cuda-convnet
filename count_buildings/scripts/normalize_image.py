import numpy as np
import subprocess
import sys
from count_buildings.libraries.calculator import round_number
from count_buildings.libraries.satellite_image import SatelliteImage
from count_buildings.libraries.satellite_image import get_dtype_bounds
from crosscompute.libraries import script
from os.path import join


OUTPUT_TYPE_BY_ARRAY_DTYPE = {
    np.dtype('uint8'): 'Byte',
    np.dtype('uint16'): 'UInt16',
    np.dtype('uint32'): 'UInt32',
}


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='')
        starter.add_argument(
            '--target_dtype', metavar='DTYPE',
            help='')
        starter.add_argument(
            '--target_meters_per_pixel_dimensions', metavar='WIDTH,HEIGHT',
            type=script.parse_dimensions,
            help='')


def run(
        target_folder, image_path, target_dtype,
        target_meters_per_pixel_dimensions):
    image = SatelliteImage(image_path)
    target_dtype = get_target_dtype(image, target_dtype)
    target_path = join(target_folder, 'image.tif')



    translate
    warp

    zoom_dimensions = get_zoom_dimensions(
        image, target_meters_per_pixel_dimensions)
    normalize(target_path, image, target_dtype, zoom_dimensions)
    return dict(
        zoom_dimensions=zoom_dimensions)


def get_target_dtype(image, target_dtype):
    if target_dtype:
        return np.dtype(target_dtype)
    else:
        return image.array_dtype


def get_pixel_dimensions(image, target_meters_per_pixel_dimensions):
    metric_dimensions = image.to_metric_dimensions(image.pixel_dimensions)
    try:
        pixel_width = round_number(metric_dimensions[0] / float(
            target_meters_per_pixel_dimensions[0]))
        pixel_height = round_number(metric_dimensions[1] / float(
            target_meters_per_pixel_dimensions[1]))
    except TypeError:
        pixel_width, pixel_height = image.pixel_dimensions
    return pixel_width, pixel_height


def translate(target_path, image, target_dtype):
    target_min, target_max = get_dtype_bounds(target_dtype)
    arguments = ['gdal_translate'] + get_gdal_options(target_dtype)
    for band_index in xrange(image.band_count):
        source_min, source_max = image.get_band_statistics(band_index)[:2]
        arguments.append('-scale_b%s %s %s %s %s' % (
            band_index + 1, source_min, source_max, target_min, target_max))
    subprocess.call(arguments + [image.path, target_path])


def warp(target_path, image, target_dtype, target_meters_per_pixel_dimensions):
    arguments = ['gdalwarp'] + get_gdal_options(target_dtype)
    pixel_dimensions = get_pixel_dimensions(
        image, target_meters_per_pixel_dimensions)
    arguments.extend([
        '-ts %s %s' % pixel_dimensions,
        '-r cubic',
        '-multi'
        '-wo NUM_THREADS=ALL_CPUS'
        '-wo OPTIMIZE_SIZE=TRUE',
        '-wo WRITE_FLUSH=YES',
        '-overwrite'])
    subprocess.call(arguments + [image.path, target_path])


def get_gdal_options(target_dtype):
    output_type = OUTPUT_TYPE_BY_ARRAY_DTYPE[target_dtype]
    return [
        '-ot %s' % output_type,
        '-of GTiff',
        '-co INTERLEAVE=BAND',
        '-co SPARSE_OK=TRUE',
        '-co COMPRESS=LZW',
        '-co PREDICTOR=%s' % (2 if output_type == 'Byte' else 3),
        '-co PHOTOMETRIC=RGB',
        '-co ALPHA=NO']
