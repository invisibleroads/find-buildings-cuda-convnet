countries = 'ethiopia0 mali0 myanmar0 senegal0 tanzania0 uganda0 uganda1'

import os
from count_buildings.libraries import satellite_image

for country in countries.split():
    image_path = os.path.join(
        os.path.expanduser('~/Links/satellite-images'), country)
    image = satellite_image.SatelliteImage(image_path)
    print 'country = %s\tband_count = %s\texample_metric_dimensions = %s' % (
        country,
        image.band_count,
        str(image.to_pixel_dimensions((10, 10))))
