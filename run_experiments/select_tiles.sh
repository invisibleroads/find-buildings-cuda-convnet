cd ~/Projects/count-buildings

# python get_tiles_from_image.py \
    # --image_path ~/Links/satellite-images/Myanmar/o12JAN12044704-S2AS-053388615010_01_P001.tif \
    # --target_folder ~/Experiments/count_buildings/abc-tiles \
    # --tile_dimensions 400x300

python get_tiles_from_image.py \
    --image_path ~/Links/satellite-images/Myanmar/o12JAN12044704-S2AS-053388615010_01_P001.tif \
    --target_folder ~/Experiments/count_buildings/abc-tiles-bounded \
    --tile_dimensions 400x300 \
    --stay_inside_pixel_bounds 13600,2400,14000,2700

# python get_tiles_from_image.py \
    # --image_path ~/Links/satellite-images/Myanmar/o12JAN12044704-S2AS-053388615010_01_P001.tif \
    # --target_folder ~/Experiments/count_buildings/abc-tiles-indexed \
    # --tile_dimensions 400x300 \
    # --tile_indices 403,404,428,429
