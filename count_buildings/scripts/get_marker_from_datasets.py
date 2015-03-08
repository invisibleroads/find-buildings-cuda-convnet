import sys
from crosscompute.libraries import script


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--batch_folder', metavar='FOLDER', required=True,
            help='')
        starter.add_argument(
            '--test_fraction', metavar='FRACTION',
            type=float, default=0.2,
            help='')
        starter.add_argument(
            '--provider_class', metavar='CLASS', required=True,
            help='')
        starter.add_argument(
            '--crop_border_pixel_length', metavar='INTEGER',
            type=int,
            help='')
        starter.add_argument(
            '--layer_definition_path', metavar='PATH', required=True,
            help='')
        starter.add_argument(
            '--layer_parameters_path', metavar='PATH', required=True,
            help='')
        starter.add_argument(
            '--patience_epoch_count', metavar='INTEGER',
            type=int, default=100,
            help='')


def run(
        target_folder, batch_folder, test_fraction,
        provider_class, crop_border_pixel_length,
        layer_definition_path, layer_parameters_path,
        patience_epoch_count):
    # Prepare class parameters
    # Run model
    return dict()


"""
# Convert function parameters to class parameters
# Identify class parameters
# Load class

from .libraries.markers.ccn import CroppedZeroMeanDataProvider
from .libraries.markers.ccn.providers import CroppedZeroMeanDataProvider
from .libraries.markers.ccn import ConvNet

data.DataProvider
op, load_dic = gpumodel.IGPUModel.parse_options(parser)
run_model(ConvNet, 'train')
def run_model(model_cls, section, cfg_filename=None):
    model = make_model(model_cls, section, cfg_filename)
    model.start()

def make_model(model_cls, section, cfg_filename=None):
    if cfg_filename is None:
        try:
            cfg_filename = sys.argv.pop(1)
        except IndexError:
            print "Provide a options configuration file as the first argument."
            sys.exit(1)
    op, load_dic, cfg = handle_options(
        parser=model_cls.get_options_parser(),
        section=section, cfg_filename=cfg_filename,
        )
    random_seed(int(cfg.get('seed', '42')))

    model = model_cls(op, load_dic)
    update_attrs_from_cfg(model, cfg, 'convnet')
    update_attrs_from_cfg(model.train_data_provider, cfg, 'dataprovider')
    update_attrs_from_cfg(model.test_data_provider, cfg, 'dataprovider')
    return model

batch_name = batches/training
test_fraction = 0.2
provider_class = CroppedZeroMeanDataProvider
crop_border_pixel_length = 4
layer_definition_path = layer-definition.cfg
layer_parameters_path = layer-parameters.cfg
patience_epoch_count = 100

--data-provider <string>        - Data provider                                                          
[--crop-border <int>           ] - Cropped DP: crop border size                         [4]               
--save-path <string>            - Save path                                                              
--layer-def <string>            - Layer definition file                                                  
--layer-params <string>         - Layer parameter file                                                   

[--mini <int>                  ] - Minibatch size                                       [128]             
[--multiview-test <0/1>        ] - Cropped DP: test on multiple patches?                [0]               
--data-path <string>            - Data path                                                              
--test-range <int[-int]>        - Data batch range: testing                                              
--train-range <int[-int]>       - Data batch range: training  

EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
OUTPUT_FOLDER=~/Experiments/$EXPERIMENT_NAME/$OUTPUT_NAME
mkdir -p $OUTPUT_FOLDER
source ~/Projects/count-buildings/run_experiments/log.sh
LOG_PATH=$OUTPUT_FOLDER/`basename $0`-$TIMESTAMP.log

MAX_TEST_BATCH_INDEX=`get_index_from_batches \
    --batches_folder $OUTPUT_FOLDER/test_batches`
MAX_TEST_BATCH_INDEX_MINUS_ONE=$(expr $MAX_TEST_BATCH_INDEX - 1)

MAX_TRAINING_BATCH_INDEX=`get_index_from_batches \
    --batches_folder $OUTPUT_FOLDER/training_batches`
MAX_TRAINING_BATCH_INDEX_MINUS_ONE=$(expr $MAX_TRAINING_BATCH_INDEX - 1)
log ccn-train options.cfg \
    --save-path $OUTPUT_FOLDER/classifiers \
    --data-path $OUTPUT_FOLDER/training_batches \
    --train-range 0-$(($MAX_TRAINING_BATCH_INDEX_MINUS_ONE > 0 ? $MAX_TRAINING_BATCH_INDEX_MINUS_ONE : 0)) \
    --test-range $MAX_TRAINING_BATCH_INDEX
CONVNET_PATH=`ls -d -t -1 $OUTPUT_FOLDER/classifiers/ConvNet__* | head -n 1`
CLASSIFIER_PATH=$OUTPUT_FOLDER/classifiers/${TIMESTAMP}
mv $CONVNET_PATH $CLASSIFIER_PATH

data-provider = count_buildings.libraries.markers.cudaconv2.CroppedZeroMeanDataProvider
crop-border=4
save-path = $HERE
layer-def = $HERE/layers.cfg
layer-params = $HERE/layer-params.cfg
give-up-epochs = 100
"""
