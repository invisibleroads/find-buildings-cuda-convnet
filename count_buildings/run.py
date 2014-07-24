import sys
from os import makedirs
from os.path import basename, join
from tempfile import mkstemp
from urllib2 import urlopen

from count_buildings.scripts.get_tiles_from_image import save_image_properties
from crosscompute.libraries import script
from crosscompute.libraries import queue


CLASSIFIER_FOLDER = '/tmp/classifiers'
DOWNLOAD_FOLDER = '/tmp/downloads'
try:
    makedirs(DOWNLOAD_FOLDER)
except OSError:
    pass


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--classifier_name', metavar='NAME', required=True)
        starter.add_argument(
            '--image_url', metavar='NAME', required=True)


def schedule(target_result_id, classifier_name, image_url):
    target_folder = script.get_target_folder(target_result_id)
    summary = run(target_folder, classifier_name, image_url)
    queue.save(target_result_id, summary)


def run(target_folder, classifier_name, image_url):
    # classifier_path = join(CLASSIFIER_FOLDER, classifier_name)
    image_path = download(image_url)
    image_name = basename(image_url)
    image_properties = save_image_properties(image_path)
    return dict(
        columns=['Dimensions', 'Bands'],
        rows=[[
            image_name,
            '%ix%im' % tuple(image_properties['image_dimensions']),
            image_properties['image_band_count']]])


def download(url):
    path = mkstemp(dir=DOWNLOAD_FOLDER)[1]
    open(path, 'wb').write(urlopen(url).read())
    return path
