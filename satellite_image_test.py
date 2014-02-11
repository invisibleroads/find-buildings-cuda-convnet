import unittest
from numpy import random

from satellite_image import Calibration


class CalibrationTest(unittest.TestCase):

    def setUp(self):
        self.calibration_pack = 1, 2, 3, 4, 5, 6
        self.calibration = Calibration(self.calibration_pack)

    def test_get_xy(self):
        xy = random.random(2)
        pixel_xy = self.calibration.get_pixel_xy(xy)
        xy_ = self.calibration.get_xy(pixel_xy)
        self.assert_((xy - xy_ < 0.0000001).all())

    def test_get_dimensions(self):
        dimensions = random.random(2)
        pixel_dimensions = self.calibration.get_pixel_dimensions(dimensions)
        dimensions_ = self.calibration.get_dimensions(pixel_dimensions)
        margin = abs(dimensions - dimensions_)
        self.assert_(margin[0] <= self.calibration_pack[1] / float(2))
        self.assert_(margin[1] <= self.calibration_pack[5] / float(2))


if __name__ == '__main__':
    unittest.main()
