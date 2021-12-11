from __future__ import annotations
from sim.sim_components import *
from sim.sim_manager import SimParams
from geometry.geometry import *
import random


def generate_city_buildings(sim_param: SimParams) -> list[Building]:
    """Generates city given the number of city blocks horizontally and vertically, and
    the width=height dimension of each block. building_cap is the approximate limit to consider
    when generating, it is not strictly enforced"""

    buildings = []

    # Constructs the city layout
    building_rects = get_city_rectangle_layout(sim_param.city_blocks_x, sim_param.city_blocks_y,
                                               sim_param.block_dim, sim_param.road_width,
                                               sim_param.buildings_constant)

    # Loops through shuffled building indexes
    for i in (lambda a: (random.shuffle(a), a)[1])(list(range(len(building_rects)))):
        # TODO: Assign Medical and Travel buildings
        # TODO: Find number of res, ind, and com buildings based on ratios and assign them
        # TODO: Implement highrise % by setting floor value of buildings
        pass

    # TODO: Return city with buildings
    return buildings


def get_city_rectangle_layout(width_blocks: int, height_blocks: int,
                              block_dim: float, road_width: float,
                              building_cap: int) -> list[Rectangle]:
    # Shuffles indexes to generate blocks at random
    w = list(range(width_blocks))
    h = list(range(height_blocks))
    random.shuffle(w)
    random.shuffle(h)

    building_rects = []

    for block_x in w:
        for block_y in h:
            # Top left corner of the current block
            left_top_of_block = Point((block_dim + road_width) * block_x,
                                      (block_dim + road_width) * block_y)

            splits = [split_block(building_cap, len(building_rects)),
                      split_block(building_cap, len(building_rects))]

            if max(splits) - min(splits) > 1:
                splits[splits.index(max(splits))] = min(splits) + 1

            # Adds rectangles of buildings
            for bld_rect in get_buildings_in_block(road_width,
                                                   block_dim,
                                                   splits[0],
                                                   splits[1],
                                                   left_top_of_block[0],
                                                   left_top_of_block[1]):
                building_rects.append(bld_rect)

    return building_rects


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
                           left: float, top: float) -> list[Rectangle]:
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

    return rects


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
