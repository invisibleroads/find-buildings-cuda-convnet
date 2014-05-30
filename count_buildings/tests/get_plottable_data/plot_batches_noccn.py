import sys
from matplotlib import pylab as plt
sys.path.append('/home/rhh/Documents/cuda-convnet')
from convdata import CIFARDataProvider


dp = CIFARDataProvider(
    '/home/rhh/Experiments/get_plottable_data/batches_noccn', [1])
batch = dp.get_next_batch()
data, labels = batch[2]

index = 7
label = labels[0][index]
print dp.batch_meta['label_names'][int(label)]
plottable_data = dp.get_plottable_data(data)
plt.imshow(plottable_data[index][:, :, :3], interpolation='nearest')
plt.show()
