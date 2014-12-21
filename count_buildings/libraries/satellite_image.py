import numpy as np
import random
import utm
from geometryIO import get_transformPoint
from osgeo import gdal, osr
from scipy.misc import toimage

from . import calculator


class ProjectedCalibration(object):

    def __init__(self, calibration_pack):
        self.calibration_pack = tuple(calibration_pack)

    def _become(self, c):
        self.calibration_pack = c.calibration_pack

    def _to_projected_width(self, pixel_width):
        g0, g1, g2, g3, g4, g5 = self.calibration_pack
        return abs(pixel_width * g1)

    def _to_pixel_width(self, projected_width):
        g0, g1, g2, g3, g4, g5 = self.calibration_pack
        return calculator.round_number(projected_width / float(g1))

    def _to_projected_height(self, pixel_height):
        g0, g1, g2, g3, g4, g5 = self.calibration_pack
        return abs(pixel_height * g5)

    def _to_pixel_height(self, projected_height):
        g0, g1, g2, g3, g4, g5 = self.calibration_pack
        return calculator.round_number(projected_height / float(g5))

    def to_projected_xy(self, (pixel_x, pixel_y)):
        'Get projected coordinates given pixel coordinates'
        g0, g1, g2, g3, g4, g5 = self.calibration_pack
        projected_x = g0 + pixel_x * g1 + pixel_y * g2
        projected_y = g3 + pixel_x * g4 + pixel_y * g5
        return np.array([projected_x, projected_y])

    def to_pixel_xy(self, (projected_x, projected_y)):
        'Get pixel coordinates given projected coordinates'
        g0, g1, g2, g3, g4, g5 = self.calibration_pack
        k = float(g1 * g5 - g2 * g4)
        x = -g0 * g5 + g2 * g3 - g2 * projected_y + g5 * projected_x
        y = -g1 * (g3 - projected_y) + g4 * (g0 - projected_x)
        return np.array([
            calculator.round_number(x / k),
            calculator.round_number(y / k)])


class MetricCalibration(ProjectedCalibration):

    def __init__(self, calibration_pack, proj4):
        super(MetricCalibration, self).__init__(calibration_pack)
        self.proj4 = proj4
        self._metric_proj4 = self._get_metric_proj4()
        self._in_metric_projection = self.proj4 == self._metric_proj4
        self._transform_to_metric_xy = get_transformPoint(
            self.proj4, self._metric_proj4)
        self._transform_to_projected_xy = get_transformPoint(
            self._metric_proj4, self.proj4)
        self._metric_xy1 = self._to_metric_xy((0, 0))

    def _become(self, c):
        super(MetricCalibration, self)._become(c)
        self.proj4 = c.proj4
        self._metric_proj4 = c._metric_proj4
        self._in_metric_projection = c._in_metric_projection
        self._transform_to_metric_xy = c._transform_to_metric_xy
        self._transform_to_projected_xy = c._transform_to_projected_xy
        self._metric_xy1 = c._to_metric_xy

    def _get_metric_proj4(self):
        if '+proj=utm' in self.proj4:
            return self.proj4
        to_ll = get_transformPoint(
            self.proj4, '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        longitude, latitude = to_ll(*self.to_projected_xy((0, 0)))
        zone_number = utm.conversion.latlon_to_zone_number(latitude, longitude)
        zone_letter = utm.conversion.latitude_to_zone_letter(latitude)
        return '+proj=utm +zone=%s%s +ellps=WGS84 +units=m +no_defs' % (
            zone_number, ' +south' if zone_letter < 'N' else '')

    def _to_metric_xy(self, (pixel_x, pixel_y)):
        'Get metric coordinates given pixel coordinates'
        projected_xy = self.to_projected_xy((pixel_x, pixel_y))
        return np.array(self._transform_to_metric_xy(*projected_xy))

    def _to_pixel_xy(self, (metric_x, metric_y)):
        'Get pixel coordinates given metric coordinates'
        projected_xy = self._transform_to_projected_xy(metric_x, metric_y)
        return self.to_pixel_xy(projected_xy)

    def to_metric_dimensions(self, (pixel_width, pixel_height)):
        'Get metric dimensions given pixel dimensions'
        if self._in_metric_projection:
            metric_width = self._to_projected_width(pixel_width)
            metric_height = self._to_projected_height(pixel_height)
        else:
            metric_xy2 = self._to_metric_xy((pixel_width, pixel_height))
            metric_width, metric_height = abs(metric_xy2 - self._metric_xy1)
        return np.array([metric_width, metric_height])

    def to_pixel_dimensions(self, (metric_width, metric_height)):
        'Get pixel dimensions given metric dimensions'
        if self._in_metric_projection:
            pixel_width = self._to_pixel_width(metric_width)
            pixel_height = self._to_pixel_height(metric_height)
        else:
            metric_xy2 = self._metric_xy1 + (metric_width, metric_height)
            pixel_width, pixel_height = abs(self._to_pixel_xy(metric_xy2))
        return np.array([pixel_width, pixel_height])


class SatelliteImage(MetricCalibration):

    def __init__(self, image_path):
        self._image = image = gdal.Open(image_path)
        super(SatelliteImage, self).__init__(
            calibration_pack=image.GetGeoTransform(), proj4=_get_proj4(image))
        self.pixel_dimensions = np.array((
            image.RasterXSize, image.RasterYSize))
        self.pixel_coordinate_dtype = np.min_scalar_type(
            max(self.pixel_dimensions))
        self.band_count = image.RasterCount
        self.band_packs = _get_band_packs(image)
        self.array_dtype = _get_array_dtype(image)
        self.null_values = [image.GetRasterBand(
            x + 1).GetNoDataValue() for x in xrange(self.band_count)]
        self.path = image_path

    def _become(self, i):
        self._image = i._image
        super(SatelliteImage, self)._become(i)
        self.pixel_dimensions = i.pixel_dimensions
        self.pixel_coordinate_dtype = i.pixel_coordinate_dtype
        self.band_count = i.band_count
        self.band_packs = i.band_packs
        self.array_dtype = i.array_dtype
        self.null_values = i.null_values
        self.path = i.path

    def _get_band_extremes(self, band_index, stddev_count=None):
        minimum, maximum, mean, stddev = self.band_packs[band_index]
        if stddev_count is None:
            return minimum, maximum
        return mean - stddev_count * stddev, mean + stddev_count * stddev

    def get_array_from_pixel_frame(
            self, (pixel_upper_left, pixel_dimensions), fill_value=0):
        pixel_x, pixel_y = pixel_upper_left
        pixel_width, pixel_height = pixel_dimensions
        try:
            array = self._image.ReadAsArray(
                pixel_x, pixel_y, pixel_width, pixel_height)
        except ValueError:
            raise ValueError('Pixel frame exceeds image bounds')
        if self.band_count > 1:
            array = np.rollaxis(array, 0, start=3)
        if len(set(self.null_values)) == 1:
            null_value = self.null_values[0]
            if null_value is not None:
                array[array == null_value] = fill_value
        else:
            for band_index in xrange(self.band_count):
                null_value = self.null_values[band_index]
                if null_value is None:
                    continue
                band_array = array[:, :, band_index]
                band_array[band_array == null_value] = fill_value
        return array

    def save_image_from_pixel_frame(
            self, target_path, (pixel_upper_left, pixel_dimensions)):
        array = self.get_array_from_pixel_frame((
            pixel_upper_left, pixel_dimensions))
        self.save_image(target_path, array)
        return array

    def save_image(self, target_path, array, band_index=None):
        target_dtype = np.dtype('uint8')
        target_min, target_max = get_dtype_bounds(target_dtype)
        if len(array.shape) == 2:
            band_index = 0
        if band_index is None:
            array = array[:, :, :3]
            for band_index in xrange(array.shape[-1]):
                source_min, source_max = self._get_band_extremes(band_index)
                array[:, :, band_index] = enhance_array(
                    array[:, :, band_index],
                    source_min, source_max, target_dtype)
        else:
            try:
                array = array[:, :, band_index]
            except IndexError:
                pass
            source_min, source_max = self._get_band_extremes(band_index)
            array = enhance_array(array, source_min, source_max, target_dtype)
        image = toimage(array, cmin=target_min, cmax=target_max)
        image.save(target_path)


class PixelScope(SatelliteImage):

    def __init__(
            self, image, tile_pixel_dimensions, overlap_pixel_dimensions=(0, 0)):
        self._become(image)
        self.tile_pixel_dimensions = np.array(tile_pixel_dimensions)
        self.overlap_pixel_dimensions = overlap_pixel_dimensions
        self.interval_pixel_dimensions = (
            self.tile_pixel_dimensions - overlap_pixel_dimensions)
        self.column_count = _chop(
            self.pixel_dimensions[0],
            self.tile_pixel_dimensions[0],
            self.interval_pixel_dimensions[0])
        self.row_count = _chop(
            self.pixel_dimensions[1],
            self.tile_pixel_dimensions[1],
            self.interval_pixel_dimensions[1])
        self.tile_count = self.column_count * self.row_count

    def get_array_from_pixel_center(self, pixel_center):
        pixel_frame = self.get_pixel_frame_from_pixel_center(pixel_center)
        return self.get_array_from_pixel_frame(pixel_frame)

    def get_array_from_pixel_upper_left(self, pixel_upper_left):
        pixel_frame = pixel_upper_left, self.tile_pixel_dimensions
        return self.get_array_from_pixel_frame(pixel_frame)

    def get_pixel_bounds_from_pixel_center(self, pixel_center):
        return get_pixel_bounds_from_pixel_center(
            pixel_center, self.tile_pixel_dimensions)

    def get_pixel_bounds_from_pixel_upper_left(self, pixel_upper_left):
        return get_pixel_bounds_from_pixel_upper_left(
            pixel_upper_left, self.tile_pixel_dimensions)

    def get_pixel_frame_from_tile_coordinates(self, (tile_column, tile_row)):
        pixel_upper_left = np.array(
            self.interval_pixel_dimensions) * (tile_column, tile_row)
        return pixel_upper_left, self.tile_pixel_dimensions

    def get_pixel_frame_from_tile_index(self, tile_index):
        tile_column = tile_index % self.column_count
        tile_row = tile_index / self.column_count
        return self.get_pixel_frame_from_tile_coordinates((
            tile_column, tile_row))

    def get_pixel_frame_from_pixel_center(self, pixel_center):
        return get_pixel_frame_from_pixel_center(
            pixel_center, self.tile_pixel_dimensions)

    def get_random_pixel_center(self):
        x1, y1 = self.minimum_pixel_center
        x2, y2 = self.maximum_pixel_center
        return np.array([
            random.randint(x1, x2),
            random.randint(y1, y2)])

    def is_pixel_center(self, pixel_center):
        x, y = pixel_center
        min_x, min_y = self.minimum_pixel_center
        max_x, max_y = self.maximum_pixel_center
        is_x = min_x <= x and x <= max_x
        is_y = min_y <= y and y <= max_y
        return is_x and is_y

    def is_pixel_upper_left(self, pixel_upper_left):
        x, y = pixel_upper_left
        min_x, min_y = self.minimum_pixel_upper_left
        max_x, max_y = self.maximum_pixel_upper_left
        is_x = min_x <= x and x <= max_x
        is_y = min_y <= y and y <= max_y
        return is_x and is_y

    @property
    def maximum_pixel_center(self):
        'Get maximum pixel_center that will return full array'
        return get_pixel_center_from_pixel_frame((
            self.maximum_pixel_upper_left, self.tile_pixel_dimensions))

    @property
    def maximum_pixel_upper_left(self):
        'Get maximum pixel_upper_left that will return full array'
        return self.pixel_dimensions - self.tile_pixel_dimensions

    @property
    def minimum_pixel_center(self):
        return get_pixel_center_from_pixel_frame((
            self.minimum_pixel_upper_left, self.tile_pixel_dimensions))

    @property
    def minimum_pixel_upper_left(self):
        return 0, 0

    def save_image_from_pixel_center(self, target_path, pixel_center):
        pixel_frame = self.get_pixel_frame_from_pixel_center(pixel_center)
        return self.save_image_from_pixel_frame(target_path, pixel_frame)

    def save_image_from_pixel_upper_left(self, target_path, pixel_upper_left):
        pixel_frame = pixel_upper_left, self.tile_pixel_dimensions
        return self.save_image_from_pixel_frame(target_path, pixel_frame)


class MetricScope(PixelScope):

    def __init__(
            self, image, tile_metric_dimensions, overlap_metric_dimensions=(0, 0)):
        tile_pixel_dimensions = image.to_pixel_dimensions(
            tile_metric_dimensions)
        overlap_pixel_dimensions = image.to_pixel_dimensions(
            overlap_metric_dimensions)
        super(MetricScope, self).__init__(
            image, tile_pixel_dimensions, overlap_pixel_dimensions)
        self.tile_metric_dimensions = tile_metric_dimensions
        self.overlap_metric_dimensions = overlap_metric_dimensions

    def get_array_from_projected_center(self, projected_center):
        pixel_center = self.to_pixel_xy(projected_center)
        return self.get_array_from_pixel_center(pixel_center)

    def get_array_from_projected_upper_left(self, projected_upper_left):
        pixel_upper_left = self.to_pixel_xy(projected_upper_left)
        return self.get_array_from_pixel_upper_left(pixel_upper_left)

    def save_image_from_projected_center(self, target_path, projected_center):
        pixel_center = self.to_pixel_xy(projected_center)
        return self.save_image_from_pixel_center(target_path, pixel_center)

    def save_image_from_projected_upper_left(
            self, target_path, projected_upper_left):
        pixel_upper_left = self.to_pixel_xy(projected_upper_left)
        return self.save_image_from_pixel_upper_left(
            target_path, pixel_upper_left)


def get_pixel_bounds_from_pixel_center(
        pixel_center, pixel_dimensions):
    pixel_frame = get_pixel_frame_from_pixel_center(
        pixel_center, pixel_dimensions)
    pixel_upper_left, pixel_dimensions = pixel_frame
    return get_pixel_bounds_from_pixel_upper_left(
        pixel_upper_left, pixel_dimensions)


def get_pixel_bounds_from_pixel_upper_left(
        pixel_upper_left, pixel_dimensions):
    pixel_lower_right = pixel_upper_left + pixel_dimensions
    return list(pixel_upper_left) + list(pixel_lower_right)


def get_pixel_frame_from_pixel_bounds(pixel_bounds):
    minimum_x, minimum_y, maximum_x, maximum_y = pixel_bounds
    pixel_upper_left = minimum_x, minimum_y
    tile_pixel_dimensions = np.array([
        (maximum_x - minimum_x),
        (maximum_y - minimum_y)])
    return pixel_upper_left, tile_pixel_dimensions


def get_pixel_frame_from_pixel_center(pixel_center, pixel_dimensions):
    pixel_upper_left = pixel_center - np.array(pixel_dimensions) / 2
    return pixel_upper_left, pixel_dimensions


def get_pixel_center_from_pixel_frame((pixel_upper_left, pixel_dimensions)):
    return pixel_upper_left + np.array(pixel_dimensions) / 2


def enhance_array(source_array, source_min, source_max, target_dtype):
    target_min, target_max = get_dtype_bounds(target_dtype)
    if source_min == target_min and source_max == target_max:
        return source_array.astype(target_dtype, copy=False)
    lookup_index = np.arange(source_max + 1) - source_min
    lookup_index *= target_max / float(lookup_index.max())
    lookup_index[:source_min] = target_min
    lookup_index = lookup_index.astype(target_dtype, copy=False)
    return np.take(lookup_index, source_array, mode='clip')


def get_dtype_bounds(dtype):
    iinfo = np.iinfo(dtype)
    return iinfo.min, iinfo.max


def _get_array_dtype(gdal_image):
    return gdal_image.ReadAsArray(0, 0, 0, 0).dtype


def _get_band_packs(image):
    'Get minimum, maximum, mean, standard deviation for each band'
    band_packs = []
    for band_number in xrange(1, image.RasterCount + 1):
        band = image.GetRasterBand(band_number)
        band_packs.append(band.GetStatistics(0, 1))
    return band_packs


def _get_proj4(image):
    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromWkt(image.GetProjectionRef())
    return spatial_reference.ExportToProj4().strip()


def _chop(canvas_length, tile_length, interval_length):
    return ((canvas_length - tile_length) / interval_length) + 1


gdal.UseExceptions()
