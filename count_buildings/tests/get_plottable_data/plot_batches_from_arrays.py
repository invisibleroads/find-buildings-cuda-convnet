import numpy as np
from matplotlib import pylab as plt
from count_buildings.libraries.markers import cudaconv2


import ipdb; ipdb.set_trace()
DataProvider = cudaconv2.CroppedZeroMeanDataProvider

dp = DataProvider(
    '/home/rhh/Experiments/get_plottable_data/get_batches_from_arrays', [0])
batch = dp.get_next_batch()
data, labels = batch[2]
pixel_height, pixel_width, band_count = dp.batch_meta['array_shape']
plottable_data = dp.get_plottable_data(data)

for index, array in enumerate(plottable_data):
    plt.imshow(array[:, :, :3], interpolation='nearest')
    plt.imsave('batch_from_array%s.jpg' % index, array[:, :, :3])
    plt.show()

# data_mean = dp.batch_meta['data_mean']
# plottable_array = np.require(data_mean.T.reshape(
    # band_count, pixel_height, pixel_width
# ).swapaxes(0, 2).swapaxes(0, 1) / 255.0, dtype=np.single)
# print plottable_array.shape  # pixel_height, pixel_width, band_count
# plt.imshow(plottable_array[:, :, :3], interpolation='nearest')
# plt.show()
