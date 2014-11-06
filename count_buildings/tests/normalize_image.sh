pushd ~/Storage/business-datasets/ColumbiaUniversity

echo uint8 0.5x0.5m
normalize_image \
    --image_path Provided/Myanmar/2014/Images/Pansharpened/oIMG_PHR1B_PMS_201401200420164_SEN_927159101-001_1_1.tif \
    --target_dtype uint8 \
    --target_meters_per_pixel_dimensions 0.5x0.5

echo uint16 0.61x0.61m
normalize_image \
    --image_path Pansharpened/Ethiopia/2006/Cell3/Images/Pansharpened/06OCT01081356-S4-005708539030_01_P001.tif \
    --target_dtype uint8 \
    --target_meters_per_pixel_dimensions 0.5x0.5

echo uint16 0.61x0.61m latitude/longitude multispectral
normalize_image \
    --image_path Original/Ethiopia/2006/Cell3/Images/Original/005708539030_01_P001_MUL/06OCT01081356-M2AS-005708539030_01_P001.TIL \
    --target_dtype uint8 \
    --target_meters_per_pixel_dimensions 0.5x0.5

echo uint16 0.61x0.61m latitude/longitude panchromatic
normalize_image \
    --image_path Original/Ethiopia/2006/Cell3/Images/Original/005708539030_01_P001_PAN/06OCT01081355-P2AS-005708539030_01_P001.TIL \
    --target_dtype uint8 \
    --target_meters_per_pixel_dimensions 0.5x0.5

echo uint32 0.6x0.6m
normalize_image \
    --image_path ~/Documents/image32.tif \
    --target_dtype uint8 \
    --target_meters_per_pixel_dimensions 0.5x0.5
