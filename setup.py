import os
from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
DESCRIPTION = '\n\n'.join(open(os.path.join(HERE, _)).read() for _ in [
    'README.md',
    'CHANGES.md',
])
REQUIREMENTS = [
    'crosscompute',
]
ENTRY_POINTS = """\
[paste.app_factory]
main = count_buildings:main
[console_scripts]
count_buildings = \
    count_buildings.run:start
get_tiles_from_image =\
    count_buildings.scripts.get_tiles_from_image:start
get_examples_from_points =\
    count_buildings.scripts.get_examples_from_points:start
get_dataset_from_examples =\
    count_buildings.scripts.get_dataset_from_examples:start
get_batches_from_datasets =\
    count_buildings.scripts.get_batches_from_datasets:start
get_marker_from_datasets =\
    count_buildings.scripts.get_marker_from_datasets:start
get_array_shape_from_batches =\
    count_buildings.scripts.get_array_shape_from_batches:start
get_index_from_batches =\
    count_buildings.scripts.get_index_from_batches:start
get_arrays_from_image =\
    count_buildings.scripts.get_arrays_from_image:start
get_batches_from_arrays =\
    count_buildings.scripts.get_batches_from_arrays:start
get_predictions_from_arrays =\
    count_buildings.scripts.get_predictions_from_arrays:start
get_counts_from_probabilities =\
    count_buildings.scripts.get_counts_from_probabilities:start
normalize_image =\
    count_buildings.scripts.normalize_image:start
train_classifier =\
    count_buildings.scripts.train_classifier:start
[crosscompute.tools]
describe = count_buildings:describe
include = count_buildings:includeme
"""


setup(
    name='count_buildings',
    version='0.1',
    description='count_buildings',
    long_description=DESCRIPTION,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Framework :: Pyramid :: CrossCompute',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Roy Hyunjin Han',
    author_email='rhh@crosscompute.com',
    url='https://crosscompute.com/count-buildings',
    keywords='web pyramid pylons crosscompute',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    entry_points=ENTRY_POINTS)
