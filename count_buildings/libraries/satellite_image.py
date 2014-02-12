import numpy as np
from functools import partial
from matplotlib import pyplot as plt
from osgeo import gdal
from osgeo import osr


_round_integer = lambda x: int(round(abs(x)))


class Calibration(object):

    def __init__(self, calibration_pack):
        self._calibration_pack = calibration_pack

    def to_xy(self, (pixel_x, pixel_y)):
        'Get geographic coordinates given pixel coordinates'
        g0, g1, g2, g3, g4, g5 = self._calibration_pack
        x = g0 + pixel_x * g1 + pixel_y * g2
        y = g3 + pixel_x * g4 + pixel_y * g5
        return x, y

    def to_pixel_xy(self, (x, y)):
        'Get pixel coordinates given geographic coordinates'
        g0, g1, g2, g3, g4, g5 = self._calibration_pack
        pixel_x = (-g0 * g5 + g2 * g3 - g2 * y + g5 * x) / (g1 * g5 - g2 * g4)
        pixel_y = (-g1 * (g3 - y) + g4 * (g0 - x)) / (g1 * g5 - g2 * g4)
        return np.array([
            _round_integer(pixel_x),
            _round_integer(pixel_y)])

    def to_dimensions(self, (pixel_width, pixel_height)):
        'Get geographic dimensions given pixel dimensions'
        g0, g1, g2, g3, g4, g5 = self._calibration_pack
        return np.array([
            abs(pixel_width * g1),
            abs(pixel_height * g5)])

    def to_pixel_dimensions(self, (width, height)):
        'Get pixel dimensions given geographic dimensions'
        g0, g1, g2, g3, g4, g5 = self._calibration_pack
        return np.array([
            _round_integer(width / float(g1)),
            _round_integer(height / float(g5))])


class SatelliteImage(Calibration):

    def __init__(self, image_path):
        image = gdal.Open(image_path)
        self._image = image
        self._vmin, self._vmax = _get_extreme_values(image)
        super(SatelliteImage, self).__init__(image.GetGeoTransform())

        self.pixel_dimensions = image.RasterXSize, image.RasterYSize
        self.spatial_reference = osr.SpatialReference()
        self.spatial_reference.ImportFromWkt(image.GetProjectionRef())
        self.proj4 = self.spatial_reference.ExportToProj4()

        self.save_array = partial(plt.imsave, vmin=self._vmin, vmax=self._vmax)

    def save_pixel_frame(self, target_path, pixel_xy, pixel_dimensions):
        array = self.get_array_from_pixel_frame(pixel_xy, pixel_dimensions)
        self.save_array(target_path, array[:, :, :3])

    def get_array_from_pixel_frame(self, pixel_xy, pixel_dimensions):
        [pixel_x, pixel_y], [
            pixel_width, pixel_height,
        ] = self._fix_pixel_frame(pixel_xy, pixel_dimensions)
        array = self._image.ReadAsArray(
            pixel_x, pixel_y, pixel_width, pixel_height)
        return np.rollaxis(array, 0, start=3)

    def _fix_pixel(self, pixel_xy):
        return np.maximum((0, 0), np.minimum(self.pixel_dimensions, pixel_xy))

    def _fix_pixel_frame(self, pixel_xy, pixel_dimensions):
        pixel_xy = np.array(pixel_xy)
        pixel_x1, pixel_y1 = self._fix_pixel(pixel_xy)
        pixel_x2, pixel_y2 = self._fix_pixel(pixel_xy + pixel_dimensions)
        return (pixel_x1, pixel_y1), (pixel_x2 - pixel_x1, pixel_y2 - pixel_y1)


class ImageScope(SatelliteImage):

    def __init__(self, image_path, scope_dimensions):
        super(ImageScope, self).__init__(image_path)
        self.scope_dimensions = scope_dimensions
        self.scope_pixel_dimensions = self.to_pixel_dimensions(
            scope_dimensions)

    def yield_pixel_xy(self, interval_pixel_dimensions):
        image_pixel_width, image_pixel_height = self.pixel_dimensions
        interval_pixel_width, interval_pixel_height = interval_pixel_dimensions
        for pixel_y in xrange(0, image_pixel_height, interval_pixel_height):
            for pixel_x in xrange(0, image_pixel_width, interval_pixel_width):
                yield pixel_x, pixel_y

    def get_array(self, center):
        pixel_center = self.to_pixel_xy(center)
        return self.get_array_from_pixel_center(pixel_center)

    def get_array_from_pixel_center(self, pixel_center):
        return self.get_array_from_pixel_frame(
            pixel_center - self.scope_pixel_dimensions / 2,
            self.scope_pixel_dimensions)

    def save_frame(self, target_path, xy):
        pixel_xy = self.to_pixel_xy(xy)
        return self.save_pixel_frame(
            target_path, pixel_xy)

    def save_pixel_frame(self, target_path, pixel_xy):
        return super(ImageScope, self).save_pixel_frame(
            target_path, pixel_xy, self.scope_pixel_dimensions)

    def get_array_from_frame(self, xy):
        pixel_xy = self.to_pixel_xy(xy)
        return self.get_array_from_pixel_frame(pixel_xy)

    def get_array_from_pixel_frame(self, pixel_xy):
        return super(ImageScope, self).get_array_from_pixel_frame


def _get_extreme_values(image):
    'Get minimum and maximum pixel values'
    band_count = image.RasterCount
    bands = [image.GetRasterBand(x + 1) for x in xrange(band_count)]
    minimums = [x.GetMinimum() for x in bands]
    maximums = [x.GetMaximum() for x in bands]
    values = [x for x in minimums + maximums if x is not None]
    return min(values), max(values)
