import numpy as np
from noccn import ccn


LabeledMemoryDataProvider = ccn.data.LabeledMemoryDataProvider


class CudaConvNetMarker(object):
    pass


class GenericDataProvider(LabeledMemoryDataProvider):

    def get_data_dims(self, idx=0):
        return self.batch_meta['num_vis'] if idx == 0 else 1

    def get_next_batch(self):
        batch = LabeledMemoryDataProvider.get_next_batch(self)
        return batch[0], batch[1], [batch[2]['data'], batch[2]['labels']]

    def get_plottable_data(self, data):
        pixel_height, pixel_width, band_count = self.batch_meta['array_shape']
        example_count = data.shape[1]
        return np.require(self.restore_data(data).T.reshape(
            example_count, band_count, pixel_height, pixel_width
        ).swapaxes(1, 3).swapaxes(1, 2) / 255.0, dtype=np.single)

    def restore_data(self, data):
        return data


class ZeroMeanDataProvider(GenericDataProvider):

    def __init__(
            self, data_dir, batch_range, init_epoch=1, init_batchnum=None,
            dp_params={}, test=False):
        GenericDataProvider.__init__(
            self, data_dir, batch_range, init_epoch, init_batchnum,
            dp_params, test)
        for d in self.data_dic:
            d['data'] = np.require(
                d['data'] - self.batch_meta['data_mean'],
                dtype=np.single, requirements='C')
            d['labels'] = np.require(
                d['labels'].reshape((1, len(d['labels']))),
                dtype=np.single, requirements='C')

    def restore_data(self, data):
        data_mean = self.batch_meta['data_mean']
        return data + data_mean


class ZeroMeanUnitVarianceDataProvider(ZeroMeanDataProvider):

    def __init__(
            self, data_dir, batch_range, init_epoch=1, init_batchnum=None,
            dp_params={}, test=False):
        ZeroMeanDataProvider.__init__(
            self, data_dir, batch_range, init_epoch, init_batchnum,
            dp_params, test)
        for d in self.data_dic:
            d['data'] = np.require(
                d['data'] / self.batch_meta['data_std'],
                dtype=np.single, requirements='C')

    def restore_data(self, data):
        data_std = self.batch_meta['data_std']
        return ZeroMeanDataProvider.restore_data(data) * data_std
