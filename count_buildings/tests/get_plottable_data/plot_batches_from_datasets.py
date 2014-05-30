from matplotlib import pylab as plt
from count_buildings.libraries.markers.cudaconv2 import ZeroMeanDataProvider


dp = ZeroMeanDataProvider(
    '/home/rhh/Experiments/get_plottable_data/get_batches_from_datasets', [0])
batch = dp.get_next_batch()
data, [labels] = batch[2]
plottable_data = dp.get_plottable_data(data)

for index, array in enumerate(plottable_data):
    label = labels[index]
    print 'label = %s' % dp.batch_meta['label_names'][int(label)]
    print 'pixel_center =', dp.batch_meta['packs'][index]
    plt.imshow(array[:, :, :3], interpolation='nearest')
    plt.show()
