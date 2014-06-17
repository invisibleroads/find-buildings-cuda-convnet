function log() {
    echo $@ | tee -a $LOG_PATH
    date | tee -a $LOG_PATH
    unbuffer $@ 2>&1 | tee -a $LOG_PATH
    date | tee -a $LOG_PATH
}
