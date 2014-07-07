OUTPUT_FOLDER=~/Storage/business-datasets/ColumbiaUniversity
SATELLITE_IMAGES=~/Links/satellite-images
BUILDING_LOCATIONS=~/Links/building-locations
mkdir -p $SATELLITE_IMAGES $BUILDING_LOCATIONS

ln -s $OUTPUT_FOLDER/Ethiopia/2005/Images/OrthorectifiedPanSharpened/KoraroQB2005.tif $SATELLITE_IMAGES/ethiopia0
ln -s $OUTPUT_FOLDER/Ethiopia/2005/Features/Buildings/KoraroQB2005Roofs.shp $BUILDING_LOCATIONS/ethiopia0

ln -s $OUTPUT_FOLDER/Mali/2005/Images/OrthorectifiedPanSharpened/TibyQB2005.tif $SATELLITE_IMAGES/mali0
ln -s $OUTPUT_FOLDER/Mali/2005/Features/Buildings/TibyQB2005Pts.shp $BUILDING_LOCATIONS/mali0

ln -s $OUTPUT_FOLDER/Myanmar/2012/Images/OrthorectifiedPanSharpened/o12JAN12044704-S2AS-053388615010_01_P001.tif $SATELLITE_IMAGES/myanmar0
ln -s $OUTPUT_FOLDER/Myanmar/2012/Features/Buildings/o12JAN12044704-S2AS-053388615010_01_P001.shp $BUILDING_LOCATIONS/myanmar0

ln -s $OUTPUT_FOLDER/Myanmar/2014/Images/OrthorectifiedPanSharpened/oIMG_PHR1B_PMS_201401200420164_SEN_927159101-001_1_1.tif $SATELLITE_IMAGES/myanmar1
ln -s $OUTPUT_FOLDER/Myanmar/2014/Features/Buildings/oIMG_PHR1B_PMS_201401200420164_SEN_927159101-001_1_1.shp $BUILDING_LOCATIONS/myanmar1

ln -s $OUTPUT_FOLDER/Myanmar/2014/Images/OrthorectifiedPanSharpened/oIMG_PHR1B_PMS_201401200420164_SEN_927159101-001_1_2.tif $SATELLITE_IMAGES/myanmar2
ln -s $OUTPUT_FOLDER/Myanmar/2014/Features/Buildings/oIMG_PHR1B_PMS_201401200420164_SEN_927159101-001_1_2.shp $BUILDING_LOCATIONS/myanmar2

ln -s $OUTPUT_FOLDER/Myanmar/2014/Images/OrthorectifiedPanSharpened/oIMG_PHR1B_PMS_201401200420164_SEN_927159101-001_2_1.tif $SATELLITE_IMAGES/myanmar3
ln -s $OUTPUT_FOLDER/Myanmar/2014/Features/Buildings/oIMG_PHR1B_PMS_201401200420164_SEN_927159101-001_2_1.shp $BUILDING_LOCATIONS/myanmar3

ln -s $OUTPUT_FOLDER/Myanmar/2014/Images/OrthorectifiedPanSharpened/oIMG_PHR1B_PMS_201401200420164_SEN_927159101-001_2_2.tif $SATELLITE_IMAGES/myanmar4
ln -s $OUTPUT_FOLDER/Myanmar/2014/Features/Buildings/oIMG_PHR1B_PMS_201401200420164_SEN_927159101-001_2_2.shp $BUILDING_LOCATIONS/myanmar4

ln -s $OUTPUT_FOLDER/Senegal/2007/Images/OrthorectifiedPanSharpened/PotouQB2007.tif $SATELLITE_IMAGES/senegal0
ln -s $OUTPUT_FOLDER/Senegal/2007/Features/Buildings/PotouPts.shp $BUILDING_LOCATIONS/senegal0

ln -s $OUTPUT_FOLDER/Tanzania/2007/Images/OrthorectifiedPanSharpened/MbolaQB2007.tif $SATELLITE_IMAGES/tanzania0
ln -s $OUTPUT_FOLDER/Tanzania/2007/Features/Buildings/MbolaPts.shp $BUILDING_LOCATIONS/tanzania0

ln -s $OUTPUT_FOLDER/Uganda/2003/Images/OrthorectifiedPanSharpened/OrthoPCSharpRuhiiraE.tif $SATELLITE_IMAGES/uganda0
ln -s $OUTPUT_FOLDER/Uganda/2003/Features/Buildings/RuhiiraE.shp $BUILDING_LOCATIONS/uganda0

ln -s $OUTPUT_FOLDER/Uganda/2007/Images/OrthorectifiedPanSharpened/OrthoPCSharpRuhiiraMV.tif $SATELLITE_IMAGES/uganda1
ln -s $OUTPUT_FOLDER/Uganda/2007/Features/Buildings/RuhiiraMV.shp $BUILDING_LOCATIONS/uganda1
