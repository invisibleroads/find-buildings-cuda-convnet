import numpy as np
import sys
from count_buildings.libraries.satellite_image import SatelliteImage
from crosscompute.libraries import script
from os.path import join
from osgeo import gdal


GDAL_DTYPE_BY_ARRAY_DTYPE = {
    np.dtype('uint8'): gdal.GDT_Byte,
    np.dtype('uint16'): gdal.GDT_UInt16,
    np.dtype('uint32'): gdal.GDT_UInt32,
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
    target_path = join(target_folder, 'image.tif')
    image = SatelliteImage(image_path)
    target_dtype = get_target_dtype(image, target_dtype)
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


def get_zoom_dimensions(image, target_meters_per_pixel_dimensions):
    metric_dimensions = image.to_metric_dimensions(image.pixel_dimensions)
    source_pixel_width, source_pixel_height = image.pixel_dimensions
    try:
        target_pixel_width = metric_dimensions[0] / float(
            target_meters_per_pixel_dimensions[0])
        target_pixel_height = metric_dimensions[1] / float(
            target_meters_per_pixel_dimensions[1])
    except TypeError:
        zoom_width = 1
        zoom_height = 1
    else:
        zoom_width = target_pixel_width / float(source_pixel_width)
        zoom_height = target_pixel_height / float(source_pixel_height)
    return zoom_width, zoom_height
