import geometryIO
import sys
from crosscompute.libraries import script


COUNTS_NAME = 'counts.shp'
PROBABILITIES_NAME = 'probabilities.csv'


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--probabilities_folder', metavar='FOLDER', required=True,
            help='')
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='satellite image')
        starter.add_argument(
            '--actual_count', metavar='INTEGER',
            type=int,
            help='')
        starter.add_argument(
            '--actual_radius', metavar='INTEGER',
            type=int,
            help='')


def run(
        target_folder, probabilities_folder, image_path, actual_count,
        actual_radius):
    target_path = os.path.join(target_folder, COUNTS_NAME)
    pixel_centers = get_pixel_centers(probabilities_folder)
    image = SatelliteImage(image_path)

    if actual_count is not None:

    centers = [image.to_xy(_) for _ in pixel_centers]
    geometryIO.save_points(target_path, image.proj4, centers)
    return dict(
        estimated_count=len(centers),
        estimated_radius=estimated_radius)


def get_pixel_centers(probabilities_folder):
    probabilities_path = os.path.join(probabilities_folder, PROBABILITIES_NAME)
    probabilities_table = read_csv(probabilities_path)
    predictions = probabilities_table[
        probabilities_table['1'] > probabilities_table['0']]
    return predictions[['pixel_center_x', 'pixel_center_y']]
