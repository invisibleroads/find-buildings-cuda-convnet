import os
import sys
from crosscompute.libraries import script

from ..libraries import satellite_image


def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='satellite image')
        starter.add_argument(
            '--tile_dimensions', metavar='WIDTH,HEIGHT',
            type=script.parse_dimensions,
            help='dimensions of extracted tile in geographic units')
        starter.add_argument(
            '--overlap_dimensions', metavar='WIDTH,HEIGHT', default=(0, 0),
            type=script.parse_dimensions,
            help='dimensions of tile overlap in geographic units')
        starter.add_argument(
            '--tile_indices', metavar='INTEGER',
            type=int, nargs='+',
            help='indices to extract')
        starter.add_argument(
            '--included_pixel_bounds', metavar='MIN_X,MIN_Y,MAX_X,MAX_Y',
            type=script.parse_bounds,
            help='target specified bounds')
        starter.add_argument(
            '--list_pixel_bounds', action='store_true',
            help='')


def run(
        target_folder, image_path,
        tile_dimensions, overlap_dimensions, tile_indices,
        included_pixel_bounds, list_pixel_bounds):
    if tile_dimensions is None and included_pixel_bounds is None:
        return save_image_dimensions(image_path)
    elif tile_dimensions is None:
        return save_pixel_bounds(
            target_folder, image_path, included_pixel_bounds)
    elif list_pixel_bounds:
        return print_pixel_bounds(
            image_path, tile_dimensions, overlap_dimensions, tile_indices,
            included_pixel_bounds)
    return save_tiles(
        target_folder, image_path,
        tile_dimensions, overlap_dimensions, tile_indices,
        included_pixel_bounds, list_pixel_bounds)


def save_image_dimensions(image_path):
    image = satellite_image.SatelliteImage(image_path)
    return dict(
        image_dimensions=image.to_dimensions(image.pixel_dimensions),
        image_pixel_dimensions=image.pixel_dimensions,
        image_band_count=image.band_count)


def save_pixel_bounds(
        target_folder, image_path, included_pixel_bounds):
    pixel_frame = [
        pixel_upper_left, pixel_dimensions
    ] = satellite_image.get_pixel_frame_from_pixel_bounds(
        included_pixel_bounds)
    image = satellite_image.SatelliteImage(image_path)

    target_path = get_tile_path(target_folder, pixel_upper_left)
    image.save_image_from_pixel_frame(target_path, pixel_frame)
    return dict(
        tile_dimensions=image.to_dimensions(pixel_dimensions),
        tile_pixel_dimensions=pixel_dimensions)


def print_pixel_bounds(
        image_path, tile_dimensions, overlap_dimensions, tile_indices,
        included_pixel_bounds):
    image_scope = satellite_image.ImageScope(image_path, tile_dimensions)
    tile_packs = image_scope.yield_tile_pack(
        overlap_dimensions, included_pixel_bounds, tile_indices)
    for tile_indices, pixel_upper_left in tile_packs:
        print '%s,%s,%s,%s' % (
            pixel_upper_left[0],
            pixel_upper_left[1],
            pixel_upper_left[0] + image_scope.scope_pixel_dimensions[0],
            pixel_upper_left[1] + image_scope.scope_pixel_dimensions[1])


def save_tiles(
        target_folder, image_path,
        tile_dimensions, overlap_dimensions, tile_indices,
        included_pixel_bounds, list_pixel_bounds):
    image_scope = satellite_image.ImageScope(image_path, tile_dimensions)
    tile_packs = list(image_scope.yield_tile_pack(
        overlap_dimensions, included_pixel_bounds, tile_indices))
    tile_count = len(tile_packs)
    tile_index = 0
    for tile_index, pixel_upper_left in tile_packs:
        if tile_index % 10 == 0:
            print '%s / %s' % (tile_index, tile_count - 1)
        array = image_scope.get_array_from_pixel_upper_left(pixel_upper_left)
        image_scope.save_image(
            get_tile_path(target_folder, pixel_upper_left, tile_index),
            array[:, :, :3])
    print '%s / %s' % (tile_index, tile_count - 1)
    return dict(
        tile_pixel_dimensions=image_scope.scope_pixel_dimensions,
        overlap_pixel_dimensions=image_scope.to_pixel_dimensions(
            overlap_dimensions))


def get_tile_path(target_folder, pixel_upper_left, tile_index=None):
    tile_name_parts = ['pul%dx%d' % pixel_upper_left]
    if tile_index is not None:
        tile_name_parts.append('i%d' % tile_index)
    tile_name = '%s.jpg' % '-'.join(tile_name_parts)
    return os.path.join(target_folder, tile_name)
