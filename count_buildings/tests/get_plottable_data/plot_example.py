import h5py
import numpy as np
import sys
example_folder = sys.argv[1]
examples_h5 = h5py.File(example_folder + '/examples.h5')
from matplotlib import pylab as plt
from skimage.transform import rescale, resize


for index, array in enumerate(examples_h5['positive']['arrays']):
    print array.shape
    print examples_h5['positive']['pixel_centers'][index]
    plt.imshow(array[:, :, :3] / 255.0)
    plt.imsave('1.png', array[:, :, :3] / 255.0)
    plt.show()
    print np.max(array)

    image = array[:, :, :3]
    pixel_height, pixel_width, band_count = array.shape
    array = resize(image, (pixel_height / 2, pixel_width / 2))
    # array = rescale(image, 0.5)
    plt.imshow(array[:, :, :3])
    plt.imsave('2.png', array[:, :, :3])
    plt.show()
    print np.max(array)
