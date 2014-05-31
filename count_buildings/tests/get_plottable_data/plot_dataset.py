import h5py
import os
import sys
dataset_folder = sys.argv[1]
country_name = sys.argv[2]
dataset_h5 = h5py.File(dataset_folder + '/dataset.h5')
from matplotlib import pylab as plt


output_folder = '/tmp/plot_dataset'
try:
    os.makedirs(output_folder)
except OSError:
    pass
for index, array in enumerate(dataset_h5['arrays']):
    label = dataset_h5['labels'][index]
    print array.shape
    print 'label = %s' % label
    print 'pixel_center =', dataset_h5['pixel_centers'][index]
    # plt.imshow(array[:, :, :3] / 255.0)
    plt.imsave(
        os.path.join(output_folder, '%s-label%s-array%s.jpg' % (
            country_name, 1 if label else 0, index)),
        array[:, :, :3] / 255.0)
    # plt.show()
