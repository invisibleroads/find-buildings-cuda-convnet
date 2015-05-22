import pickle
import shutil
import subprocess
import sys
from glob import glob
from os import makedirs, remove
from os.path import abspath, basename, dirname, expanduser, join, splitext

from crosscompute.libraries import disk
from crosscompute.libraries import queue
from crosscompute.libraries import script
from crosscompute.models import Result, get_data_path


CENTS_PER_SQUARE_KILOMETER = 50
CLASSIFIER_FOLDER = expanduser('~/Documents/classifiers')
DOWNLOAD_FOLDER = expanduser('~/Documents/downloads')
try:
    makedirs(DOWNLOAD_FOLDER)
except OSError:
    pass
PACKAGE_FOLDER = dirname(dirname(abspath(__file__)))
SCRIPT_FOLDER = join(PACKAGE_FOLDER, 'run_experiments/20141231-2344')
SCRIPT_PATH = join(SCRIPT_FOLDER, 'manage_scan.sh')


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--image_path', metavar='PATH', required=True)
        starter.add_argument(
            '--classifier_name', metavar='NAME', required=True)


def schedule(
        target_result_id, source_geoimage_id, classifier_name, is_preview):
    target_folder = Result(id=target_result_id).target_folder
    p53_path = get_data_path('p53')
    try:
        remove(p53_path)
    except OSError:
        pass
    disk.make_folder(target_folder)

    result = Result(id=source_geoimage_id)
    result.download()

    if is_preview:
        summary = {'preview_image_names': [], 'estimated_counts': []}
        for image_index, image_path in enumerate(sorted(
                glob(join(result.target_folder, 'preview*.tif')))):
            s = run(target_folder, image_path, classifier_name, is_preview=True)
            summary['estimated_counts'].append(s['estimated_count'])

            preview_image_name = splitext(basename(image_path))[0] + '.jpg'
            target_preview_image_path = join(target_folder, preview_image_name)
            try:
                shutil.move(
                    join(target_folder, 'preview.jpg'),
                    target_preview_image_path)
            except IOError:
                shutil.copy(
                    join(result.target_folder, preview_image_name),
                    target_preview_image_path)
            summary['preview_image_names'].append(preview_image_name)
    else:
        image_path = join(result.target_folder, 'image.tif')
        summary = run(
            target_folder, image_path, classifier_name, is_preview=False)

    queue.save(target_result_id, summary)
    open(p53_path, 'wt')


def run(target_folder, image_path, classifier_name, is_preview=False):
    classifier_path = join(CLASSIFIER_FOLDER, classifier_name)
    subprocess.call([
        'bash', SCRIPT_PATH, target_folder, classifier_path, image_path])
    run_properties = pickle.load(open(join(target_folder, 'run.pkl')))
    estimated_count = run_properties['variables']['estimated_count']

    if is_preview:
        for file_path in glob(join(target_folder, 'counts.*')):
            try:
                remove(file_path)
            except OSError:
                pass

    return dict(
        estimated_count=estimated_count,
        preview_image_name='preview.jpg')


def price(area_in_square_meters):
    area_in_square_kilometers = area_in_square_meters / float(1000 * 1000)
    return round(CENTS_PER_SQUARE_KILOMETER * area_in_square_kilometers)
