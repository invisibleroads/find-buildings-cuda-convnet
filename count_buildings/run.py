import sys
from os import makedirs
from os.path import basename, expanduser, join
from tempfile import mkstemp
from urllib2 import urlopen

from count_buildings.scripts.get_tiles_from_image import save_image_properties
from crosscompute import models
from crosscompute.libraries import disk
from crosscompute.libraries import queue
from crosscompute.libraries import script
from crosscompute.models import Result, get_data_path


CLASSIFIER_FOLDER = expanduser('~/Documents/classifiers')
DOWNLOAD_FOLDER = expanduser('~/Documents/downloads')
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
    target_folder = Result(id=target_result_id).target_folder
    p53_path = get_data_path('p53')
    try:
        os.remove(p53_path)
    except OSError:
        pass
    disk.make_folder(target_folder)
    summary = run(target_folder, classifier_name, image_url)
    queue.save(target_result_id, summary)
    open(p53_path, 'wt')


def run(target_folder, classifier_name, image_url):
    classifier_path = join(CLASSIFIER_FOLDER, classifier_name)
    image_path = download(image_url)
    image_name = basename(image_url)
    image_properties = save_image_properties(image_path)

    import subprocess
    subprocess.call([
        'bash',
        '/home/ec2-user/Projects/count-buildings/run_experiments/20140724-1114/myanmar/manage_scan.sh',
        target_folder, classifier_path, image_path])

    import pickle
    run_properties = pickle.load(open(join(target_folder, 'run.pkl')))
    estimated_count = run_properties['variables']['estimated_count']

    return dict(
        columns=['Dimensions', 'Bands', 'Count'],
        rows=[[
            '%ix%im' % tuple(image_properties['image_dimensions']),
            image_properties['image_band_count'],
            estimated_count]])


def download(url):
    path = mkstemp(dir=DOWNLOAD_FOLDER)[1]
    open(path, 'wb').write(urlopen(url).read())
    return path
