import os
from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
DESCRIPTION = '\n\n'.join(open(os.path.join(HERE, _)).read() for _ in [
    'README.md',
    'CHANGES.md',
])
REQUIREMENTS = [
] + [
]
ENTRY_POINTS = """\
[console_scripts]
get_tiles_from_image = count_buildings.scripts.get_tiles_from_image:go
"""


setup(
    name='count_buildings',
    version='0.0.1',
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
    test_suite='count_buildings',
    tests_require=REQUIREMENTS,
    install_requires=REQUIREMENTS,
    entry_points=ENTRY_POINTS)
