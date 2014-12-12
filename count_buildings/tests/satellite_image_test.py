import numpy as np
import unittest
from geometryIO import proj4LL
from mock import MagicMock
from numpy import random

from ..libraries.satellite_image import ProjectedCalibration
from ..libraries.satellite_image import MetricCalibration
from ..libraries.satellite_image import _get_array


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

    def setUp(self):
        pass

    def test_get_array(self):
        pixel_frame = (0, 0), (10, 10)
        # Pixel frame exceeds image bounds
        gdal_image = MagicMock()
        gdal_image.ReadAsArray.side_effect = ValueError
        self.assertRaises(
            ValueError, _get_array, gdal_image, pixel_frame)
        # Image has multiple spectral bands
        gdal_image = MagicMock()
        gdal_array_shape = 6, 4, 5
        gdal_image.RasterCount = 3
        gdal_image.ReadAsArray.return_value = np.random.rand(*gdal_array_shape)
        self.assertEqual(
            _get_array(gdal_image, pixel_frame).shape,
            gdal_array_shape[-2:] + gdal_array_shape[:-2])
        # make void value only not be none and be only one
        gdal_image = MagicMock()
        gdal_image.RasterCount = 1
        gdal_image.ReadAsArray.return_value = np.array([0, 1, 2])
        gdal_image.GetRasterBand.return_value.GetNoDataValue.return_value = 2
        self.assert_((
            _get_array(gdal_image, pixel_frame) == np.array([0, 1, 0])).all())
        # make there be many void values, but one of which is none
        gdal_image = MagicMock()
        gdal_image.RasterCount = 2
        gdal_image.ReadAsArray.return_value = np.array([
            [[2, 2], [2, 2]], [[2, 2], [2, 2]]])
        gdal_image.GetRasterBand.return_value.GetNoDataValue.side_effect = (
            2, None)
        self.assert_((
            _get_array(gdal_image, pixel_frame) == np.array([
                [[0, 2], [0, 2]], [[0, 2], [0, 2]]])).all())


if __name__ == '__main__':
    unittest.main()
