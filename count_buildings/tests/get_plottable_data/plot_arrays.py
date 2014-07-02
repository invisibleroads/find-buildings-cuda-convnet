import h5py
arrays_h5 = h5py.File(
    '/home/rhh/Experiments/get_plottable_data/arrays/arrays.h5')
from matplotlib import pylab as plt

array = arrays_h5['arrays'][0]
print array.shape
print arrays_h5['pixel_centers'][0]

plt.imshow(array[:, :, :3] / 255.0)
# plt.imsave('array.jpg', array[:, :, :3])
plt.show()
