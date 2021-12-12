from geometry.geometry import *
from geometry.helpers import *
import random


def get_city_rectangle_layout(width_blocks: int, height_blocks: int,
                              block_dim: float, road_width: float,
                              building_cap: int) -> tuple[list[Rectangle], float]:
    """
    Return list of rectangles for where the buildings will be located. Also return the
    smallest road width among local roads between blocks (used for path finding parameters)

    :return: building rectangles, smallest local road width
    """
    building_rects = []

    for block_x in get_shuffled(list(range(width_blocks))):
        for block_y in get_shuffled(list(range(height_blocks))):
            # Top left corner of the current block
            left_top_of_block = Point((block_dim + road_width) * block_x,
                                      (block_dim + road_width) * block_y)

            splits = [split_block(building_cap, len(building_rects)),
                      split_block(building_cap, len(building_rects))]

            if max(splits) - min(splits) > 1:
                splits[splits.index(max(splits))] = min(splits) + 1

            # Adds rectangles of buildings
            buildings_in_block, smallest_road_width = get_buildings_in_block(road_width,
                                                                               block_dim,
                                                                               splits[0],
                                                                               splits[1],
                                                                               left_top_of_block[0],
                                                                               left_top_of_block[1])
            for bld_rect in buildings_in_block:
                building_rects.append(bld_rect)

    return building_rects, smallest_road_width


def split_block(cap: int, buildings_so_far: int) -> int:
    """Given the number of buildings in the city so far, and an approximate desired
    building cap, run a randomizer to see how many times a city block should be
    split. The less buildings so far, the higher the chance it will split, to make more
    buildings."""
    splits = 0
    # Initial chance to split once, multiplied to the function based on building count
    chance = 0.8

    f = ((-100 / cap) * buildings_so_far) + 100
    while random.randint(1, 100) <= f * chance:
        splits += 1
        # Decreases the chance of a subsequent split
        chance *= 0.4

    return splits


def get_buildings_in_block(road_width: float, block_dim: float, splits_w: int, splits_h: int,
                           left: float, top: float) -> tuple[list[Rectangle], float]:
    local_road_width_w = road_width * 0.75 ** (splits_w + 1)
    local_road_width_h = road_width * 0.75 ** (splits_h + 1)

    building_w = (block_dim - splits_w * local_road_width_w) / (splits_w + 1)
    building_h = (block_dim - splits_h * local_road_width_h) / (splits_h + 1)

    rects = []

    for i in range(splits_w + 1):
        for j in range(splits_h + 1):
            rects.append(Rectangle(left=left + i * (building_w + local_road_width_w),
                                   top=top + j * (building_h + local_road_width_h),
                                   width=building_w, height=building_h))

    return rects, min(local_road_width_h, local_road_width_w)


def _avg_buildings(width_blocks: int, height_blocks: int, building_cap: int, sims=1000):
    """Used to find the number of buildings that appear on average for given city gen parameters"""
    sim_values = []

    for _ in range(sims):
        buildings = 0

        for i in range(width_blocks * height_blocks):
            buildings += (split_block(building_cap, buildings) + 1) * \
                         (split_block(building_cap, buildings) + 1)

        sim_values.append(buildings)

    return round(sum(sim_values) / len(sim_values), 2)
