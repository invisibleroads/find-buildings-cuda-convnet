import os
import sys
import numpy as np


sys.path.append(os.path.expanduser('~/Documents/cuda-convnet'))
from data import LabeledMemoryDataProvider


class CudaConvNetMarker(object):
    pass


class ZeroMeanDataProvider(LabeledMemoryDataProvider):

    def __init__(
            self, data_dir, batch_range, init_epoch=1, init_batchnum=None,
            dp_params={}, test=False):
        LabeledMemoryDataProvider.__init__(
            self, data_dir, batch_range, init_epoch, init_batchnum,
            dp_params, test)
        self.data_mean = self.batch_meta['data_mean']
        for d in self.data_dic:
            d['data'] = np.require(
                d['data'] - self.data_mean,
                dtype=np.single, requirements='C')
            d['labels'] = np.require(
                d['labels'].reshape((1, d['data'].shape[1])),
                dtype=np.single, requirements='C')

    def get_next_batch(self):
        batch = LabeledMemoryDataProvider.get_next_batch(self)
        return batch[0], batch[1], [batch[2]['data'], batch[2]['labels']]

    def get_data_dims(self, idx=0):
        return self.batch_meta['num_vis'] if idx == 0 else 1
