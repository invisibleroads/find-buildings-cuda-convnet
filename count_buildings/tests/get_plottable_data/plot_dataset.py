import h5py
import sys
dataset_folder = sys.argv[1]
dataset_h5 = h5py.File(dataset_folder + '/dataset.h5')
from matplotlib import pylab as plt

for index, array in enumerate(dataset_h5['arrays']):
    print array.shape
    print 'label = %s' % dataset_h5['labels'][index]
    print 'pixel_center =', dataset_h5['pixel_centers'][index]
    plt.imshow(array[:, :, :3] / 255.0)
    plt.show()
