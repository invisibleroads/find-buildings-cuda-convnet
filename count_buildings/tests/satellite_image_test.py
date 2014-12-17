import numpy as np
import unittest
from geometryIO import proj4LL
from mock import patch
from numpy import random
from osgeo.osr import SpatialReference

from ..libraries.satellite_image import ProjectedCalibration
from ..libraries.satellite_image import MetricCalibration
from ..libraries.satellite_image import SatelliteImage


LIBRARY_ROUTE = 'count_buildings.libraries.satellite_image'
spatial_reference = SpatialReference()
spatial_reference.ImportFromEPSG(4326)
WKT = spatial_reference.ExportToWkt()
PIXEL_FRAME = (0, 0), (10, 10)
CALIBRATION_PACK = 0, 0.5, 0, 0, 0, -0.5


class ProjectedCalibrationTest(unittest.TestCase):

    def setUp(self):
        self.calibration_pack = 1, 2, 3, 4, 5, 6
        self.calibration = ProjectedCalibration(self.calibration_pack)

    def test_to_projected_xy(self):
        old_projected_xy = random.random(2)
        new_projected_xy = self.calibration.to_projected_xy(
            self.calibration.to_pixel_xy(old_projected_xy))
        self.assert_((old_projected_xy - new_projected_xy < 0.0000001).all())


class MetricCalibrationTest(unittest.TestCase):

    def setUp(self):
        self.calibration_pack = 1, 2, 3, 4, 5, 6
        self.calibration = MetricCalibration(self.calibration_pack, proj4LL)

    def test_to_metric_dimensions(self):
        old_metric_dimensions = random.random(2)
        new_metric_dimensions = self.calibration.to_metric_dimensions(
            self.calibration.to_pixel_dimensions(old_metric_dimensions))
        margin = abs(old_metric_dimensions - new_metric_dimensions)
        self.assert_(margin[0] <= self.calibration_pack[1] / float(2))
        self.assert_(margin[1] <= self.calibration_pack[5] / float(2))


class SatelliteImageTest(unittest.TestCase):

    @patch(LIBRARY_ROUTE + '.gdal')
    def test_get_array_from_pixel_frame_outside_image_bounds(self, mock_gdal):
        gdal_image = get_gdal_image(mock_gdal)
        image = SatelliteImage('/tmp/image.tif')
        gdal_image.ReadAsArray.side_effect = ValueError
        self.assertRaises(
            ValueError, image.get_array_from_pixel_frame, PIXEL_FRAME)

    @patch(LIBRARY_ROUTE + '.gdal')
    def test_get_array_from_pixel_frame_with_many_bands(self, mock_gdal):
        gdal_image = get_gdal_image(mock_gdal)
        gdal_image.RasterCount = 3
        image = SatelliteImage('/tmp/image.tif')
        gdal_array_shape = 6, 4, 5
        gdal_image.ReadAsArray.return_value = np.random.rand(*gdal_array_shape)
        array = image.get_array_from_pixel_frame(PIXEL_FRAME)
        expected_array_shape = gdal_array_shape[-2:] + gdal_array_shape[:-2]
        self.assertEqual(array.shape, expected_array_shape)

    @patch(LIBRARY_ROUTE + '.gdal')
    def test_get_array_from_pixel_frame_with_one_null_value(self, mock_gdal):
        gdal_image = get_gdal_image(mock_gdal)
        gdal_band = gdal_image.GetRasterBand
        gdal_band.return_value.GetNoDataValue.return_value = 2
        image = SatelliteImage('/tmp/image.tif')
        gdal_image.ReadAsArray.return_value = np.array([0, 1, 2])
        array = image.get_array_from_pixel_frame(PIXEL_FRAME)
        expected_array = np.array([0, 1, 0])
        self.assert_((array == expected_array).all())

    @patch(LIBRARY_ROUTE + '.gdal')
    def test_get_array_from_pixel_frame_with_many_null_values(self, mock_gdal):
        gdal_image = get_gdal_image(mock_gdal)
        gdal_image.RasterCount = 2
        gdal_band = gdal_image.GetRasterBand
        gdal_band.return_value.GetNoDataValue.side_effect = 2, None
        image = SatelliteImage('/tmp/image.tif')
        gdal_image.ReadAsArray.return_value = np.array([
            [[2, 2], [2, 2]], [[2, 2], [2, 2]]])
        array = image.get_array_from_pixel_frame(PIXEL_FRAME)
        expected_array = np.array([[[0, 2], [0, 2]], [[0, 2], [0, 2]]])
        self.assert_((array == expected_array).all())


def get_gdal_image(mock_gdal):
    gdal_image = mock_gdal.Open.return_value
    gdal_image.GetProjectionRef.return_value = WKT
    gdal_image.GetGeoTransform.return_value = CALIBRATION_PACK
    return gdal_image


if __name__ == '__main__':
    unittest.main()
