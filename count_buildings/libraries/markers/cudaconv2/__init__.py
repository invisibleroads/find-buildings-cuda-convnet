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


class CroppedZeroMeanDataProvider(ZeroMeanDataProvider):

    def __init__(
            self, data_dir, batch_range, init_epoch=1, init_batchnum=None,
            dp_params=None, test=False):
        ZeroMeanDataProvider.__init__(
            self, data_dir, batch_range, init_epoch, init_batchnum,
            dp_params, test)
        self.pixel_height, self.pixel_width, self.band_count = self.batch_meta['array_shape']

        self.border_size = dp_params['crop_border']
        self.inner_height = pixel_height - self.border_size * 2
        self.inner_width = pixel_width - self.border_size * 2

        self.multiview = dp_params['multiview_test'] and test
        self.num_views = 5 * 2
        self.data_mult = self.num_views if self.multiview else 1

        for d in self.data_dic:
            d['labels'] = n.require(n.tile(d['labels'].reshape((1, d['data'].shape[1])), (1, self.data_mult)), requirements='C')

        self.cropped_data = [
            n.zeros((self.get_data_dims(), self.data_dic[0]['data'].shape[1] * self.data_mult), dtype=n.single) for x in xrange(2)]

        self.batches_generated = 0
        self.data_mean = self.batch_meta['data_mean'].T.reshape((self.band_count, self.pixel_height, self.pixel_width))[
            :,
            self.border_size:self.border_size+self.inner_height,
            self.border_size:self.border_size+self.inner_width,
        ].reshape((self.get_data_dims(), 1))

    def get_next_batch(self):
        epoch, batchnum, datadic = ZeroMeanDataProvider.get_next_batch(self)

        cropped = self.cropped_data[self.batches_generated % 2]

        self.__trim_borders(datadic['data'], cropped)
        cropped -= self.data_mean
        self.batches_generated += 1
        return epoch, batchnum, [cropped, datadic['labels']]

    def get_data_dims(self, idx=0):
        return self.inner_height * self.inner_width * self.band_count if idx == 0 else 1

    def get_plottable_data(self, data):
        return n.require((data + self.data_mean).T.reshape(data.shape[1], self.band_count, self.inner_height, self.inner_width).swapaxes(1,3).swapaxes(1,2) / 255.0, dtype=n.single)

    def __trim_borders(self, x, target):
        y = x.reshape(self.band_count, self.pixel_height, self.pixel_width, x.shape[1])

        if self.test: # don't need to loop over cases
            if self.multiview:
                start_positions = [(0,0),  (0, self.border_size*2),
                                   (self.border_size, self.border_size),
                                  (self.border_size*2, 0), (self.border_size*2, self.border_size*2)]
                end_positions = [(sy+self.inner_height, sx+self.inner_width) for (sy,sx) in start_positions]
                for i in xrange(self.num_views/2):
                    pic = y[:,start_positions[i][0]:end_positions[i][0],start_positions[i][1]:end_positions[i][1],:]
                    target[:,i * x.shape[1]:(i+1)* x.shape[1]] = pic.reshape((self.get_data_dims(),x.shape[1]))
                    target[:,(self.num_views/2 + i) * x.shape[1]:(self.num_views/2 +i+1)* x.shape[1]] = pic[:,:,::-1,:].reshape((self.get_data_dims(),x.shape[1]))
            else:
                pic = y[:,self.border_size:self.border_size+self.inner_height,self.border_size:self.border_size+self.inner_width, :] # just take the center for now
                target[:,:] = pic.reshape((self.get_data_dims(), x.shape[1]))
        else:
            for c in xrange(x.shape[1]): # loop over cases
                startY, startX = nr.randint(0,self.border_size*2 + 1), nr.randint(0,self.border_size*2 + 1)
                endY, endX = startY + self.inner_height, startX + self.inner_width
                pic = y[:,startY:endY,startX:endX, c]
                if nr.randint(2) == 0: # also flip the image with 50% probability
                    pic = pic[:,:,::-1]
                target[:,c] = pic.reshape((self.get_data_dims(),))
