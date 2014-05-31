BASE_FOLDER=`pwd`
# cd $BASE_FOLDER/layers-19pct; ccn-train options.cfg
cd $BASE_FOLDER/layers-conv-local-11pct-crop3-wc0-200k; ccn-train options.cfg
cd $BASE_FOLDER/layers-conv-local-11pct-crop3-wc0-200k-dropout-layers1; ccn-train options.cfg
cd $BASE_FOLDER/layers-conv-local-11pct-crop3-wc0-200k-dropout-layers2; ccn-train options.cfg
