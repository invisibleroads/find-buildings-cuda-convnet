import numpy as np
import struct
from osgeo import gdal
from osgeo import osr


class SatelliteImage(object):

    def __init__(self, image_path):
        self._image = gdal.Open(image_path)
        self.pixel_dimensions = (
            self._image.RasterXSize,
            self._image.RasterYSize)
        self.calibration = self._image.GetGeoTransform()
        self.spatial_reference = osr.SpatialReference()
        self.spatial_reference.ImportFromWkt(
            self._image.GetProjectionRef())
        self.proj4 = self.spatial_reference.ExportToProj4()

    def get_array_from_pixel_frame(self, pixel_xy, pixel_dimensions):
        [
            pixel_x,
            pixel_y,
        ], [
            pixel_width,
            pixel_height,
        ] = self.fix_pixel_frame(pixel_xy, pixel_dimensions)
        value_count = pixel_width * pixel_height
        arrays = []
        for band_index in xrange(self._image.RasterCount):
            band = self._image.GetRasterBand(band_index + 1)
            value_format = {
                gdal.GDT_Byte: 'B',
                gdal.GDT_UInt16: 'H',
            }[band.DataType]
            values = struct.unpack(
                '%d%s' % (value_count, value_format),
                band.ReadRaster(pixel_x, pixel_y, pixel_width, pixel_height))
            arrays.append(np.reshape(values, (pixel_height, pixel_width)))
        return np.dstack(arrays)

    def fix_pixel(self, pixel_xy):
        return np.maximum((0, 0), np.minimum(self.pixel_dimensions, pixel_xy))

    def fix_pixel_frame(self, pixel_xy, pixel_dimensions):
        pixel_xy = np.array(pixel_xy)
        pixel_x1, pixel_y1 = self.fix_pixel(pixel_xy)
        pixel_x2, pixel_y2 = self.fix_pixel(pixel_xy + pixel_dimensions)
        return (pixel_x1, pixel_y1), (pixel_x2 - pixel_x1, pixel_y2 - pixel_y1)

    def get_pixel_xy(self, xy):
        return self.calibration.get_pixel_xy(xy)

    def get_xy(self, pixel_xy):
        return self.calibration.get_xy(pixel_xy)


class ImageScope(object):

    def __init__(self, satellite_image, dimensions):
        self.satellite_image = satellite_image
        self.dimensions = dimensions
        self.pixel_dimensions = satellite_image.get_pixel_dimensions(
            dimensions)

    def get_centers(self):
        pass

    def get_array(self, center):
        pixel_center = self.satellite_image.get_pixel_xy(center)
        return self.get_array_from_pixel_center(pixel_center)

    def get_array_from_pixel_center(self, pixel_center):
        pixel_xy = pixel_center - self.pixel_dimensions / 2
        return self.satellite_image.get_array_from_pixel_frame(
            pixel_xy, self.pixel_dimensions)


class MixedImageScope(ImageScope):

    def __init__(self, satellite_images, meter_dimensions, mix):
        make_scope = lambda x: ImageScope(x, meter_dimensions)
        self.scopes = [make_scope(x) for x in satellite_images]
        self.mix = mix

    def get_array(self, center):
        arrays = [x.get_array(center) for x in self.scopes]
        return self.mix(arrays)


class Calibration(object):

    def __init__(self, calibration_pack):
        self.calibration_pack = calibration_pack

    def get_xy(self, (pixel_x, pixel_y)):
        'Get geographic coordinates given pixel coordinates'
        g0, g1, g2, g3, g4, g5 = self.calibration_pack
        x = g0 + pixel_x * g1 + pixel_y * g2
        y = g3 + pixel_x * g4 + pixel_y * g5
        return x, y

    def get_pixel_xy(self, (x, y)):
        'Get pixel coordinates given geographic coordinates'
        g0, g1, g2, g3, g4, g5 = self.calibration_pack
        pixel_x = (-g0 * g5 + g2 * g3 - g2 * y + g5 * x) / (g1 * g5 - g2 * g4)
        pixel_y = (-g1 * (g3 - y) + g4 * (g0 - x)) / (g1 * g5 - g2 * g4)
        return pixel_x, pixel_y

    def get_dimensions(self, (pixel_width, pixel_height)):
        'Get geographic dimensions given pixel dimensions'
        g0, g1, g2, g3, g4, g5 = self.calibration_pack
        return np.array([
            abs(pixel_width * g1),
            abs(pixel_height * g5)])

    def get_pixel_dimensions(self, (width, height)):
        'Get pixel dimensions given geographic dimensions'
        g0, g1, g2, g3, g4, g5 = self.calibration_pack
        cast = lambda x: int(round(abs(x)))
        return np.array([
            cast(width / float(g1)),
            cast(height / float(g5))])
