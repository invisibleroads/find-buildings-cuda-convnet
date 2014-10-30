import numpy as np
import sys
from count_buildings.libraries.satellite_image import SatelliteImage
from count_buildings.libraries.calculator import round_number
from crosscompute.libraries import script
from os.path import join
from osgeo import gdal
from scipy.ndimage.interpolation import zoom


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


def normalize(target_path, image, target_dtype, (zoom_width, zoom_height)):
    source_gdal_dataset = image._image
    target_gdal_dataset = gdal.GetDriverByName('GTiff').Create(
        target_path,
        round_number(image.pixel_dimensions[0] * zoom_width),
        round_number(image.pixel_dimensions[1] * zoom_height),
        image.band_count, GDAL_DTYPE_BY_ARRAY_DTYPE[target_dtype])
    target_gdal_dataset.SetGeoTransform(zoom_calibration_pack(
        image.calibration_pack, (zoom_width, zoom_height)))
    target_gdal_dataset.SetProjection(source_gdal_dataset.GetProjection())
    for band_number, band in yield_band(source_gdal_dataset):
        enhanced_array = enhance_array(band.ReadAsArray(), target_dtype)
        rescaled_array = zoom(enhanced_array, (zoom_height, zoom_width))
        target_band = target_gdal_dataset.GetRasterBand(band_number)
        target_band.WriteArray(rescaled_array)
    target_gdal_dataset.FlushCache()


def yield_band(gdal_dataset):
    band_count = gdal_dataset.RasterCount
    for band_number in xrange(1, band_count + 1):
        yield band_number, gdal_dataset.GetRasterBand(band_number)


def enhance_array(source_array, target_dtype):
    source_min, source_max = source_array.min(), source_array.max()
    target_min, target_max = get_dtype_bounds(target_dtype)
    if source_min == target_min and source_max == target_max:
        return source_array.astype(target_dtype, copy=False)
    lookup_index = np.arange(source_max + 1) - source_min
    lookup_index *= target_max / float(lookup_index.max())
    lookup_index = lookup_index.astype(target_dtype, copy=False)
    return np.take(lookup_index, source_array)


def get_dtype_bounds(dtype):
    iinfo = np.iinfo(dtype)
    return iinfo.min, iinfo.max


def zoom_calibration_pack(calibration_pack, (zoom_width, zoom_height)):
    g0, g1, g2, g3, g4, g5 = calibration_pack
    return g0, g1 / float(zoom_width), g2, g3, g4, g5 / float(zoom_height)
