import numpy as np
import os
import shlex
import subprocess
import sys
from count_buildings.libraries.satellite_image import SatelliteImage
from count_buildings.libraries.satellite_image import get_dtype_bounds
from invisibleroads_macros.calculator import round_number
from crosscompute.libraries import script
from os.path import abspath, join
from tempfile import mkstemp


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
    band_extremes = image.band_extremes
    source_pixel_dimensions = image.pixel_dimensions
    target_dtype = get_target_dtype(image, target_dtype)
    target_pixel_dimensions = get_pixel_dimensions(
        image, target_meters_per_pixel_dimensions)
    target_path = join(target_folder, 'image.tif')
    temporary_path = mkstemp('.tif')[1]
    gdal_options = get_gdal_options(image.band_count)
    null_values = image.null_values
    del image
    # Warp
    if should_warp(
            source_pixel_dimensions,
            target_pixel_dimensions, null_values):
        warp(
            temporary_path, image_path, gdal_options,
            target_pixel_dimensions, null_values)
    else:
        temporary_path = image_path
    # Translate
    if should_translate(
            band_extremes, target_dtype):
        translate(
            target_path, temporary_path, gdal_options,
            band_extremes, target_dtype)
    else:
        os.symlink(abspath(temporary_path), target_path)
    # Return
    return dict(
        pixel_dimensions=target_pixel_dimensions)


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


def should_warp(source_pixel_dimensions, target_pixel_dimensions, null_values):
    if tuple(source_pixel_dimensions) != tuple(target_pixel_dimensions):
        return True
    if set(null_values) - set([None, 0]):
        return True
    return False


def warp(
        target_image_path, source_image_path, gdal_options,
        target_pixel_dimensions, null_values):
    gdal_warp_args = list(gdal_options) + [
        '-ts %s %s' % target_pixel_dimensions,
        '-srcnodata "%s"' % ' '.join(str(v) for v in null_values),
        '-dstnodata "%s"' % ' '.join('0' for x in xrange(len(null_values))),
        '-r cubic',
        '-multi',
        '-wo NUM_THREADS=ALL_CPUS',
        '-wo OPTIMIZE_SIZE=TRUE',
        '-wo WRITE_FLUSH=YES',
        '-overwrite']
    launch('gdalwarp', gdal_warp_args + [
        source_image_path, target_image_path])


def should_translate(band_extremes, target_dtype):
    target_min, target_max = get_dtype_bounds(target_dtype)
    for band_index in xrange(len(band_extremes)):
        source_min, source_max = band_extremes[band_index]
        if source_min != target_min or source_max != target_max:
            return True
    return False


def translate(
        target_image_path, source_image_path, gdal_options,
        band_extremes, target_dtype):
    target_min, target_max = get_dtype_bounds(target_dtype)
    gdal_translate_args = list(gdal_options) + [
        '-ot %s' % OUTPUT_TYPE_BY_ARRAY_DTYPE[target_dtype],
        '-a_nodata none',
    ]
    for band_index in xrange(len(band_extremes)):
        source_min, source_max = band_extremes[band_index]
        gdal_translate_args.append('-scale_%s %s %s %s %s' % (
            band_index + 1, source_min, source_max, target_min, target_max))
    launch('gdal_translate', gdal_translate_args + [
        source_image_path, target_image_path])


def get_gdal_options(band_count):
    return [
        '-of GTiff',
        '-co INTERLEAVE=BAND',
        '-co SPARSE_OK=TRUE',
        '-co COMPRESS=LZW',
        '-co PREDICTOR=2',
        '-co PHOTOMETRIC=%s' % ('RGB' if band_count >= 3 else 'MINISBLACK'),
        '-co ALPHA=NO',
        '-co BIGTIFF=YES']


def launch(command, options):
    command_string = ' '.join([command] + options)
    print(command_string)
    subprocess.check_call(shlex.split(command_string))
