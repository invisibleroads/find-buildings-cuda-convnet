cd ~/Storage/bits/markers
while :; do
    TIMESTAMP=`python -c "import datetime; print(datetime.datetime.now().strftime('%Y%m%d-%H%M'))"`
    FILE_NAME=generic-$TIMESTAMP.tar.gz
    echo $FILE_NAME
    tar czvf $FILE_NAME generic
    cp $FILE_NAME ~/Documents/Dropbox
    sleep 60 * 60 * 12;
done
