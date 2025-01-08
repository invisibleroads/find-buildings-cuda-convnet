This project has been deprecated. Please see the following link for the latest work:
https://crosscompute.com/n/DAyIrX65pdVFri4rUfDntj2NqT219PoC

This project builds off earlier work:
https://github.com/invisibleroads/find-buildings-gblearn2

Find buildings using cuda-convnet
=================================
Reveal population density.


Run scripts
-----------

    get_tiles_from_image.py
    get_points_from_tiles.py

    get_examples_from_points.py
    get_dataset_from_examples.py
    get_batches_from_datasets.py
    get_marker_from_dataset.py

    get_array_shape_from_batches.py
    get_index_from_batches.py

    get_arrays_from_image.py
    get_batches_from_arrays.py
    get_predictions_from_arrays.py
    get_counts_from_predictions.py


Launch interface
----------------

    ENV=~/.virtualenvs/crosscompute
    virtualenv $ENV
    source $ENV/bin/activate
    pip install -U crosscompute

    cd ~/Projects/count-buildings
    python setup.py develop
    pserve development.ini
