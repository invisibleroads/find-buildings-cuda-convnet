BASE_FOLDER=`pwd`
cd $BASE_FOLDER/layer_parameters/conv-local-11pct/crop3-wc0; ccn-train options.cfg
cd $BASE_FOLDER/layer_parameters/conv-local-11pct/crop3-wc0/dropout-layers1; ccn-train options.cfg
cd $BASE_FOLDER/layer_parameters/conv-local-11pct/crop3-wc0/dropout-layers2; ccn-train options.cfg
cd $BASE_FOLDER/layer_parameters/19pct; ls; ccn-train options.cfg
