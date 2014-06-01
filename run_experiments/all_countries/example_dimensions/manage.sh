BASE_FOLDER=`pwd`
cd $BASE_FOLDER/7x7; bash run.sh; ccn-train options.cfg
cd $BASE_FOLDER/10x10; bash run.sh; ccn-train options.cfg
cd $BASE_FOLDER/12x12; bash run.sh; ccn-train options.cfg
cd $BASE_FOLDER/19x19; bash run.sh; ccn-train options.cfg
