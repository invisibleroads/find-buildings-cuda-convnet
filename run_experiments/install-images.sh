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

ln -s $OUTPUT_FOLDER/Ethiopia/2005/Images/OrthorectifiedPanSharpened/KoraroQB2005.tif ~/Links/satellite-images/ethiopia0
ln -s $OUTPUT_FOLDER/Ethiopia/2005/Features/Buildings/KoraroQB2005Roofs.shp ~/Links/building-locations/ethiopia0

ln -s $OUTPUT_FOLDER/Mali/2005/Images/OrthorectifiedPanSharpened/TibyQB2005.tif ~/Links/satellite-images/mali0
ln -s $OUTPUT_FOLDER/Mali/2005/Features/Buildings/TibyQB2005Pts.shp ~/Links/building-locations/mali0

ln -s $OUTPUT_FOLDER/Myanmar/2012/Images/OrthorectifiedPanSharpened/o12JAN12044704-S2AS-053388615010_01_P001.tif ~/Links/satellite-images/myanmar0
ln -s $OUTPUT_FOLDER/Myanmar/2012/Features/Buildings/o12JAN12044704-S2AS-053388615010_01_P001.shp ~/Links/building-locations/myanmar0

ln -s $OUTPUT_FOLDER/Senegal/2007/Images/OrthorectifiedPanSharpened/PotouQB2007.tif ~/Links/satellite-images/senegal0
ln -s $OUTPUT_FOLDER/Senegal/2007/Features/Buildings/PotouPts.shp ~/Links/building-locations/senegal0

ln -s $OUTPUT_FOLDER/Tanzania/2007/Images/OrthorectifiedPanSharpened/MbolaQB2007.tif ~/Links/satellite-images/tanzania0
ln -s $OUTPUT_FOLDER/Tanzania/2007/Features/Buildings/MbolaPts.shp ~/Links/building-locations/tanzania0

ln -s $OUTPUT_FOLDER/Uganda/2003/Images/OrthorectifiedPanSharpened/OrthoPCSharpRuhiiraE.tif ~/Links/satellite-images/uganda0
ln -s $OUTPUT_FOLDER/Uganda/2003/Features/Buildings/RuhiiraE.shp ~/Links/building-locations/uganda0

ln -s $OUTPUT_FOLDER/Uganda/2007/Images/OrthorectifiedPanSharpened/OrthoPCSharpRuhiiraMV.tif ~/Links/satellite-images/uganda1
ln -s $OUTPUT_FOLDER/Uganda/2007/Features/Buildings/RuhiiraMV.shp ~/Links/building-locations/uganda1
