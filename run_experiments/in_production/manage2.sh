BASE_FOLDER=`pwd`
CLASSIFIERS="
generic
mali
tanzania
ethiopia
"
for CLASSIFIER in $CLASSIFIERS; do
    cd $BASE_FOLDER/$CLASSIFIER
    ccn-train options.cfg
done
