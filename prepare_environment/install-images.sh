OUTPUT_FOLDER=~/Storage/business-datasets/ColumbiaUniversity
mkdir -p $OUTPUT_FOLDER
cd $OUTPUT_FOLDER

wget http://backpack.invisibleroads.com/count-buildings/images/Ethiopia.tar.gz
wget http://backpack.invisibleroads.com/count-buildings/images/Kenya.tar.gz
wget http://backpack.invisibleroads.com/count-buildings/images/Mali.tar.gz
wget http://backpack.invisibleroads.com/count-buildings/images/Myanmar.tar.gz
wget http://backpack.invisibleroads.com/count-buildings/images/Senegal.tar.gz
wget http://backpack.invisibleroads.com/count-buildings/images/Tanzania.tar.gz
wget http://backpack.invisibleroads.com/count-buildings/images/Uganda.tar.gz

tar xzvf Ethiopia.tar.gz
tar xzvf Kenya.tar.gz
tar xzvf Mali.tar.gz
tar xzvf Myanmar.tar.gz
tar xzvf Senegal.tar.gz
tar xzvf Tanzania.tar.gz
tar xzvf Uganda.tar.gz

bash install-links.sh
