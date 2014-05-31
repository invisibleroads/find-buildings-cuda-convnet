BASE_FOLDER=`pwd`
# cd $BASE_FOLDER/layers-19pct; ccn-train options.cfg
cd $BASE_FOLDER/layers-conv-local-11pct/200k/crop3-wc0; ccn-train options.cfg
cd $BASE_FOLDER/layers-conv-local-11pct/200k/crop3-wc0/dropout-layers1; ccn-train options.cfg
cd $BASE_FOLDER/layers-conv-local-11pct/200k/crop3-wc0/dropout-layers2; ccn-train options.cfg
