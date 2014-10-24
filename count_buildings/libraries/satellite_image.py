import math
import numpy as np
import random
import utm
from geometryIO import get_transformPoint
from itertools import product
from matplotlib import pyplot as plt
from osgeo import gdal, osr

from . import calculator


class ProjectedCalibration(object):

    def __init__(self, calibration_pack):
        self._calibration_pack = tuple(calibration_pack)

    @property
    def calibration_pack(self):
        return self._calibration_pack

    def to_projected_xy(self, (pixel_x, pixel_y)):
        'Get projected coordinates given pixel coordinates'
        g0, g1, g2, g3, g4, g5 = self._calibration_pack
        projected_x = g0 + pixel_x * g1 + pixel_y * g2
        projected_y = g3 + pixel_x * g4 + pixel_y * g5
        return np.array([projected_x, projected_y])

    def to_pixel_xy(self, (projected_x, projected_y)):
        'Get pixel coordinates given projected coordinates'
        g0, g1, g2, g3, g4, g5 = self._calibration_pack
        k = float(g1 * g5 - g2 * g4)
        x = -g0 * g5 + g2 * g3 - g2 * projected_y + g5 * projected_x
        y = -g1 * (g3 - projected_y) + g4 * (g0 - projected_x)
        return np.array([
            calculator.round_number(x / k),
            calculator.round_number(y / k)])

    def _to_projected_width(self, pixel_width):
        g0, g1, g2, g3, g4, g5 = self._calibration_pack
        return abs(pixel_width * g1)

    def _to_pixel_width(self, projected_width):
        g0, g1, g2, g3, g4, g5 = self._calibration_pack
        return calculator.round_number(projected_width / float(g1))

    def _to_projected_height(self, pixel_height):
        g0, g1, g2, g3, g4, g5 = self._calibration_pack
        return abs(pixel_height * g5)

    def _to_pixel_height(self, projected_height):
        g0, g1, g2, g3, g4, g5 = self._calibration_pack
        return calculator.round_number(projected_height / float(g5))


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
        image = gdal.Open(image_path)
        self._image = image
        self._vmin, self._vmax = _get_extreme_values(image)
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromWkt(image.GetProjectionRef())
        super(SatelliteImage, self).__init__(
            calibration_pack=image.GetGeoTransform(),
            proj4=spatial_reference.ExportToProj4().strip())
        self.pixel_dimensions = np.array((
            image.RasterXSize, image.RasterYSize))
        self.pixel_coordinate_dtype = np.min_scalar_type(
            max(self.pixel_dimensions))
        self.band_count = image.RasterCount
        self.array_dtype = self._get_array_dtype()

    def _get_array_dtype(self):
        return self._image.ReadAsArray(0, 0, 0, 0).dtype

    def save_image(self, target_path, array):
        kw = dict(vmin=self._vmin, vmax=self._vmax)
        try:
            array = array[:, :, :3]
        except IndexError:
            kw['cmap'] = plt.cm.Greys_r
        return plt.imsave(target_path, array, **kw)

    def save_image_from_pixel_frame(
            self, target_path, (pixel_upper_left, pixel_dimensions)):
        array = self.get_array_from_pixel_frame((
            pixel_upper_left, pixel_dimensions))
        self.save_image(target_path, array)
        return array

    def get_array_from_pixel_frame(self, (pixel_upper_left, pixel_dimensions)):
        pixel_width, pixel_height = pixel_dimensions
        array = self._get_clipped_array((pixel_upper_left, pixel_dimensions))
        is_clipped = array.shape[-2:] != (pixel_height, pixel_width)
        try:
            array = np.rollaxis(array, 0, start=3)
        except ValueError:
            if is_clipped:
                padded_array = np.zeros((
                    pixel_height, pixel_width),
                    dtype=array.dtype)
                padded_array[
                    :array.shape[0], :array.shape[1]] = array
                array = padded_array
        else:
            if is_clipped:
                padded_array = np.zeros((
                    pixel_height, pixel_width, array.shape[-1]),
                    dtype=array.dtype)
                padded_array[
                    :array.shape[0], :array.shape[1], :array.shape[2]] = array
                array = padded_array
        return array

    def _get_clipped_array(self, (pixel_upper_left, pixel_dimensions)):
        pixel_upper_left = np.array(pixel_upper_left)
        pixel_x1, pixel_y1 = self._clip_pixel_xy(
            pixel_upper_left)
        pixel_x2, pixel_y2 = self._clip_pixel_xy(
            pixel_upper_left + pixel_dimensions)
        return self._image.ReadAsArray(
            pixel_x1, pixel_y1, pixel_x2 - pixel_x1, pixel_y2 - pixel_y1)

    def _clip_pixel_xy(self, pixel_xy):
        return np.maximum((0, 0), np.minimum(self.pixel_dimensions, pixel_xy))


class ImageScope(SatelliteImage):

    def __init__(self, image_path, scope_metric_dimensions):
        super(ImageScope, self).__init__(image_path)
        self.scope_metric_dimensions = scope_metric_dimensions
        self.scope_pixel_dimensions = self.to_pixel_dimensions(
            scope_metric_dimensions)

    def yield_tile_pack(
            self, overlap_metric_dimensions,
            pixel_bounds=None, tile_indices=None):
        image_pixel_width, image_pixel_height = self.pixel_dimensions
        interval_pixel_dimensions = self.to_pixel_dimensions(
            self.scope_metric_dimensions - overlap_metric_dimensions)
        interval_pixel_width, interval_pixel_height = interval_pixel_dimensions
        min_pixel_x, min_pixel_y = 0, 0
        max_pixel_x, max_pixel_y = self.pixel_dimensions
        try:
            pixel_x1, pixel_y1, pixel_x2, pixel_y2 = pixel_bounds
        except TypeError:
            pixel_x1, pixel_y1 = min_pixel_x, min_pixel_y
            pixel_x2, pixel_y2 = max_pixel_x, max_pixel_y
        pixel_x_iter = get_covering_xrange(
            pixel_x1, pixel_x2, interval_pixel_width,
            min_pixel_x, max_pixel_x)
        pixel_y_iter = get_covering_xrange(
            pixel_y1, pixel_y2, interval_pixel_height,
            min_pixel_y, max_pixel_y)
        row_count = get_row_count(image_pixel_height, interval_pixel_height)
        for pixel_upper_left in product(pixel_x_iter, pixel_y_iter):
            tile_index = get_tile_index(
                pixel_upper_left, interval_pixel_dimensions, row_count)
            if tile_indices and tile_index not in tile_indices:
                continue
            yield tile_index, pixel_upper_left

    def save_image_from_projected_center(self, target_path, projected_center):
        pixel_center = self.to_pixel_xy(projected_center)
        return self.save_image_from_pixel_center(target_path, pixel_center)

    def save_image_from_pixel_center(self, target_path, pixel_center):
        pixel_frame = self.get_pixel_frame_from_pixel_center(pixel_center)
        return self.save_image_from_pixel_frame(target_path, pixel_frame)

    def save_image_from_projected_upper_left(
            self, target_path, projected_upper_left):
        pixel_upper_left = self.to_pixel_xy(projected_upper_left)
        return self.save_image_from_pixel_upper_left(
            target_path, pixel_upper_left)

    def save_image_from_pixel_upper_left(self, target_path, pixel_upper_left):
        pixel_frame = pixel_upper_left, self.scope_pixel_dimensions
        return self.save_image_from_pixel_frame(target_path, pixel_frame)

    def get_array_from_projected_center(self, projected_center):
        pixel_center = self.to_pixel_xy(projected_center)
        return self.get_array_from_pixel_center(pixel_center)

    def get_array_from_pixel_center(self, pixel_center):
        pixel_frame = self.get_pixel_frame_from_pixel_center(pixel_center)
        return self.get_array_from_pixel_frame(pixel_frame)

    def get_array_from_projected_upper_left(self, projected_upper_left):
        pixel_upper_left = self.to_pixel_xy(projected_upper_left)
        return self.get_array_from_pixel_upper_left(pixel_upper_left)

    def get_array_from_pixel_upper_left(self, pixel_upper_left):
        pixel_frame = pixel_upper_left, self.scope_pixel_dimensions
        return self.get_array_from_pixel_frame(pixel_frame)

    def get_pixel_bounds_from_pixel_center(self, pixel_center):
        return get_pixel_bounds_from_pixel_center(
            pixel_center, self.scope_pixel_dimensions)

    def get_pixel_bounds_from_pixel_upper_left(self, pixel_upper_left):
        return get_pixel_bounds_from_pixel_upper_left(
            pixel_upper_left, self.scope_pixel_dimensions)

    def get_pixel_frame_from_pixel_center(self, pixel_center):
        return get_pixel_frame_from_pixel_center(
            pixel_center, self.scope_pixel_dimensions)

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

    @property
    def minimum_pixel_center(self):
        return get_pixel_center_from_pixel_frame((
            self.minimum_pixel_upper_left, self.scope_pixel_dimensions))

    @property
    def maximum_pixel_center(self):
        'Get maximum pixel_center that will return full array'
        return get_pixel_center_from_pixel_frame((
            self.maximum_pixel_upper_left, self.scope_pixel_dimensions))

    def is_pixel_upper_left(self, pixel_upper_left):
        x, y = pixel_upper_left
        min_x, min_y = self.minimum_pixel_upper_left
        max_x, max_y = self.maximum_pixel_upper_left
        is_x = min_x <= x and x <= max_x
        is_y = min_y <= y and y <= max_y
        return is_x and is_y

    @property
    def minimum_pixel_upper_left(self):
        return 0, 0

    @property
    def maximum_pixel_upper_left(self):
        'Get maximum pixel_upper_left that will return full array'
        return self.pixel_dimensions - self.scope_pixel_dimensions


def _get_extreme_values(image):
    'Get minimum and maximum pixel values'
    band_count = image.RasterCount
    bands = [image.GetRasterBand(x + 1) for x in xrange(band_count)]
    minimums = [x.GetMinimum() for x in bands]
    maximums = [x.GetMaximum() for x in bands]
    try:
        values = [x for x in minimums + maximums if x is not None]
        return min(values), max(values)
    except ValueError:
        values = [band.ComputeRasterMinMax() for band in bands]
        return np.min(values), np.max(values)


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


def get_covering_xrange(a, b, interval, minimum, maximum):
    a_cover = int(math.ceil(-1 + a / float(interval)) * interval)
    b_cover = int(math.floor(+1 + b / float(interval)) * interval)
    return xrange(max(a_cover, minimum), min(b_cover, maximum + 1), interval)


def get_tile_index(pixel_upper_left, interval_pixel_dimensions, row_count):
    pixel_x, pixel_y = pixel_upper_left
    interval_pixel_x, interval_pixel_y = interval_pixel_dimensions
    return row_count * pixel_x / interval_pixel_x + pixel_y / interval_pixel_y


def get_row_count(height, interval_y):
    return int(math.ceil(height / float(interval_y)))


gdal.UseExceptions()
