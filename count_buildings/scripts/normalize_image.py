import numpy as np
import subprocess
import sys
from count_buildings.libraries.calculator import round_number
from count_buildings.libraries.satellite_image import SatelliteImage
from count_buildings.libraries.satellite_image import get_dtype_bounds
from crosscompute.libraries import script
from os.path import join
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
    # Prepare
    image = SatelliteImage(image_path)
    target_dtype = get_target_dtype(image, target_dtype)
    target_min, target_max = get_dtype_bounds(target_dtype)
    target_pixel_dimensions = get_pixel_dimensions(
        image, target_meters_per_pixel_dimensions)
    target_path = join(target_folder, 'image.tif')
    band_count = image.band_count
    band_extremes = [image.get_band_statistics(
        x)[:2] for x in xrange(band_count)]
    translated_path = mkstemp('.tif')[1]
    del image
    if the range has already been expanded badn_extremes
        then make link for translated_path to original image_path

    if resolution is the same pixel_dimensions  
        hten make link for target_path to translated_path

    # Translate
    if should_translate():
        pass
    else:
        pass
    gdal_translate_args = get_gdal_options(target_dtype)
    for band_index in xrange(band_count):
        source_min, source_max = band_extremes[band_index]
        gdal_translate_args.append('-scale_%s %s %s %s %s' % (
            band_index + 1, source_min, source_max, target_min, target_max))
    launch('gdal_translate', gdal_translate_args, image_path, translated_path)
    # Warp
    if should_warp():
        pass
    else:
        pass
    gdal_warp_args = get_gdal_options(target_dtype) + [
        '-ts %s %s' % target_pixel_dimensions,
        '-r cubic',
        '-multi -wo NUM_THREADS=ALL_CPUS',
        '-wo OPTIMIZE_SIZE=TRUE',
        '-wo WRITE_FLUSH=YES',
        '-overwrite']
    launch('gdalwarp', gdal_warp_args, translated_path, target_path)
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


def get_gdal_options(target_dtype):
    return [
        '-ot %s' % OUTPUT_TYPE_BY_ARRAY_DTYPE[target_dtype],
        '-of GTiff',
        '-co INTERLEAVE=BAND',
        '-co SPARSE_OK=TRUE',
        '-co COMPRESS=LZW -co PREDICTOR=2',
        '-co PHOTOMETRIC=RGB -co ALPHA=NO',
        '-co BIGTIFF=YES']


def launch(command, options, source_path, target_path):
    command_string = ' '.join([command] + options + [source_path, target_path])
    print command_string
    subprocess.call(command_string.split())
