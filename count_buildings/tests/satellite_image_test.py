import unittest
from geometryIO import proj4LL
from numpy import random

from ..libraries.satellite_image import ProjectedCalibration
from ..libraries.satellite_image import MetricCalibration


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


if __name__ == '__main__':
    unittest.main()
