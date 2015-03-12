import numpy as np
import os
import sys
from os.path import join

from invisibleroads_macros.calculator import get_percent_change


CCN_FOLDER = os.getenv('CUDA_CONVNET', join(
    os.getenv('VIRTUAL_ENV'), 'opt/cuda-convnet'))
sys.path.append(CCN_FOLDER)


import convnet
from data import DataProvider, LabeledDataProvider
from gpumodel import IGPUModel
from options import IntegerOptionParser


class ConvNet(convnet.ConvNet):

    patience_epoch_count = 10

    def conditional_save(self):
        'Save checkpoint only if test error decreased'
        last_layer = self.layers[-1]['name']
        train_size = len(self.train_batch_range)
        train_mean = np.array([
            e[0][last_layer][0] for e in self.train_outputs[-train_size:]
        ]).mean()
        print 'Train error last %d batches: %.6f' % (train_size, train_mean)

        if self.has_var('best_test_error'):
            best_test_error = self.get_var('best_test_error')
            best_test_info = self.get_var('best_test_info')
        else:
            best_test_error = None

        this_test_error = self.test_outputs[-1][0][last_layer][0]
        if best_test_error and this_test_error >= best_test_error:
            print '-' * 64
            print 'Not saving because %.6f > %.6f (%s)' % (
                this_test_error, best_test_error, best_test_info)
            print '=' * 64
            best_epoch = int(self.get_var('best_test_info').split('.', 1)[0])
            if best_epoch < self.epoch - self.patience_epoch_count:
                print 'Patience exhausted'
                sys.exit(0)
        else:
            self.set_var('best_test_error', this_test_error)
            self.set_var('best_test_info', '%d.%d: %.2f%%' % (
                self.epoch, self.batchnum,
                get_percent_change(this_test_error, best_test_error)))
            convnet.ConvNet.conditional_save(self)

    def start(self):
        if self.test_only:
            self.test_outputs += [self.get_test_error()]
            self.print_test_results()
            sys.exit(0)
        if self.testing_freq == 1:
            self.test_outputs += [self.get_test_error()]
            self.print_test_results()
        self.train()

    @classmethod
    def get_options_parser(Class):
        try:
            return Class._options_parser
        except AttributeError:
            pass
        options_parser = convnet.ConvNet.get_options_parser()
        options_parser.add_option(
            'patience-epoch-count', 'patience_epoch_count',
            IntegerOptionParser, 'Patience epoch count', default=10)
        Class._options_parser = options_parser
        return options_parser


class GenericDataProvider(LabeledDataProvider):

    def get_data_dims(self, idx=0):
        return self.batch_meta['num_vis'] if idx == 0 else 1

    def get_next_batch(self):
        epoch_index, batch_index, d = LabeledDataProvider.get_next_batch(self)
        data, labels, count = d['data'], d['labels'], len(d['labels'])
        data = np.require(
            data,
            dtype=np.single, requirements='C')
        labels = np.require(
            np.array(labels).reshape((1, count)),
            dtype=np.single, requirements='C')
        return epoch_index, batch_index, [data, labels]

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
        self.data_mean = self.batch_meta['data_mean']

    def get_next_batch(self):
        epoch_index, batch_index, [
            data, labels,
        ] = GenericDataProvider.get_next_batch(self)
        data = np.require(
            data - self.data_mean,
            dtype=np.single, requirements='C')
        return epoch_index, batch_index, [data, labels]

    def restore_data(self, data):
        return data + self.data_mean


class CroppedZeroMeanDataProvider(ZeroMeanDataProvider):

    def __init__(
            self, data_dir, batch_range, init_epoch=1, init_batchnum=None,
            dp_params=None, test=False):
        ZeroMeanDataProvider.__init__(
            self, data_dir, batch_range, init_epoch, init_batchnum,
            dp_params, test)
        [
            self.pixel_height, self.pixel_width, self.band_count,
        ] = self.batch_meta['array_shape']
        self.border_size = dp_params['crop_border']
        self.inner_height = self.pixel_height - self.border_size * 2
        self.inner_width = self.pixel_width - self.border_size * 2

        self.multiview = dp_params['multiview_test'] and test
        self.num_views = 5 * 2
        self.data_mult = self.num_views if self.multiview else 1

        self.cropped_data_mean = self.batch_meta['data_mean'].T.reshape(
            (self.band_count, self.pixel_height, self.pixel_width)
        )[
            :,
            self.border_size:self.border_size + self.inner_height,
            self.border_size:self.border_size + self.inner_width,
        ].reshape((self.get_data_dims(), 1))

    def get_next_batch(self):
        epoch_index, batch_index, [
            data, labels,
        ] = ZeroMeanDataProvider.get_next_batch(self)
        cropped_data = np.require(
            np.zeros((self.get_data_dims(), data.shape[1] * self.data_mult)),
            dtype=np.single, requirements='C')
        self.__trim_borders(data, cropped_data)
        labels = np.require(
            np.tile(labels, (1, self.data_mult)),
            dtype=np.single, requirements='C')
        return epoch_index, batch_index, [cropped_data, labels]

    def get_data_dims(self, idx=0):
        inner_area = self.inner_height * self.inner_width
        return inner_area * self.band_count if idx == 0 else 1

    def get_plottable_data(self, data):
        band_count = self.band_count
        pixel_height, pixel_width = self.inner_height, self.inner_width
        example_count = data.shape[1]
        return np.require(self.restore_data(data).T.reshape(
            example_count, band_count, pixel_height, pixel_width
        ).swapaxes(1, 3).swapaxes(1, 2) / 255.0, dtype=np.single)

    def __trim_borders(self, x, target):
        y = x.reshape(
            self.band_count, self.pixel_height, self.pixel_width, x.shape[1])

        if self.test:  # don't loop over cases
            if self.multiview:
                start_positions = [
                    (0, 0),
                    (0, self.border_size * 2),
                    (self.border_size, self.border_size),
                    (self.border_size * 2, 0),
                    (self.border_size * 2, self.border_size * 2)]
                end_positions = [(
                    sy + self.inner_height,
                    sx + self.inner_width,
                ) for (sy, sx) in start_positions]
                for i in xrange(self.num_views/2):
                    pic = y[
                        :,
                        start_positions[i][0]:end_positions[i][0],
                        start_positions[i][1]:end_positions[i][1],
                        :]
                    target[
                        :,
                        i * x.shape[1]:(i + 1) * x.shape[1],
                    ] = pic.reshape((
                        self.get_data_dims(), x.shape[1]))
                    target[
                        :,
                        (self.num_views / 2 + i) * x.shape[1]:(
                            self.num_views / 2 + i + 1) * x.shape[1],
                    ] = pic[:, :, ::-1, :].reshape((
                        self.get_data_dims(), x.shape[1]))
            else:
                pic = y[
                    :,
                    self.border_size:self.border_size + self.inner_height,
                    self.border_size:self.border_size + self.inner_width,
                    :]  # just take the center for now
                target[:, :] = pic.reshape((self.get_data_dims(), x.shape[1]))
        else:
            for c in xrange(x.shape[1]):  # loop over cases
                startY = np.random.randint(0, self.border_size * 2 + 1)
                startX = np.random.randint(0, self.border_size * 2 + 1)
                endY = startY + self.inner_height
                endX = startX + self.inner_width
                pic = y[:, startY:endY, startX:endX, c]
                if np.random.randint(2) == 0:  # flip with 50% probability
                    pic = pic[:, :, ::-1]
                target[:, c] = pic.reshape((self.get_data_dims(),))

    def restore_data(self, cropped_data):
        return cropped_data + self.cropped_data_mean


def get_model_arguments(
        target_folder, batch_folder,
        training_batch_range, testing_batch_range,
        data_provider, crop_border_pixel_length,
        layer_definition_path, layer_parameters_path,
        patience_epoch_count):
    old_arguments = sys.argv
    sys.argv = sys.argv[:1] + [
        '--save-path=%s' % target_folder,
        '--data-path=%s' % batch_folder,
        '--train-range=%s-%s' % training_batch_range,
        '--test-range=%s-%s' % testing_batch_range,
        '--data-provider=%s' % data_provider,
        '--crop-border=%s' % crop_border_pixel_length,
        '--layer-def=%s' % layer_definition_path,
        '--layer-params=%s' % layer_parameters_path,
        '--patience-epoch-count=%s' % patience_epoch_count,
    ]
    options_parser = ConvNet.get_options_parser()
    options_parser, value_by_key = IGPUModel.parse_options(options_parser)
    sys.argv = old_arguments
    return options_parser, value_by_key


DataProvider.register_data_provider(
    'generic', 'generic', GenericDataProvider)
DataProvider.register_data_provider(
    'zero-mean', 'zero-mean', ZeroMeanDataProvider)
DataProvider.register_data_provider(
    'cropped-zero-mean', 'cropped-zero-mean', CroppedZeroMeanDataProvider)
