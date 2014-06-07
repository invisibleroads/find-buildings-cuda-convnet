LOG_PATH=$OUTPUT_FOLDER/run.log
function log() {
    echo $@ | tee -a $LOG_PATH
    date | tee -a $LOG_PATH
    $@ 2>&1 | tee -a $LOG_PATH
    date | tee -a $LOG_PATH
}
