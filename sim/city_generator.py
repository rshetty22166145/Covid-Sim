from __future__ import annotations
from sim.sim_components import *
from sim.sim_manager import *
from geometry.helpers import average, generate_integers_with_average
from sim.city_generator_helpers import *
import random


def generate_city_people(sim_manager: SimManager, sim_param: SimParams) -> set[Person]:
    """Generates people in the city given the simulation parameters. People are
    generated randomly and cannot be strictly defined"""
    # Gets population individual ages
    ages = generate_integers_with_average(18, 85, sim_param.avg_age, sim_param.population)
    # Gets population individual mask wearing tendency
    mask_wearing_percentages = generate_integers_with_average(0, 100, sim_param.mask_wearing_percentage,
                                                              sim_param.population)

    num_vaccinated = min(int(sim_param.population * (sim_param.initial_vaccination_percentage / 100)),
                         sim_param.population)
    num_infected = min(int(sim_param.population * (sim_param.initial_infection_percentage / 100)),
                       sim_param.population)
    num_homeless = min(int(sim_param.population * (sim_param.homelessness_percentage / 100)),
                       sim_param.population)

    # Gets population individual vaccination, infection, and homelessness status
    vaccination_booleans = get_shuffled(([True] * num_vaccinated) +
                                        ([False] * (sim_param.population - num_vaccinated)))
    infection_booleans = get_shuffled(([True] * num_infected) +
                                      ([False] * (sim_param.population - num_infected)))
    homelessness_booleans = get_shuffled(([True] * num_homeless) +
                                         ([False] * (sim_param.population - num_homeless)))

    people = set()
    for i in range(sim_param.population):
        people.add(Person(sim_manager, ages[i], mask_wearing_percentages[i], vaccination_booleans[i],
                          infection_booleans[i], homelessness_booleans[i], sim_param.average_travels_per_year))

    return people


def generate_city_buildings(sim_manager: SimManager, sim_param: SimParams) -> tuple[set[Building], float]:
    """Generates city buildings given the simulation parameters. City is generated randomly
    and cannot be strictly defined"""

    buildings = set()

    # Constructs the city layout
    building_rects, smallest_road_width = get_city_rectangle_layout(sim_param.city_blocks_x, sim_param.city_blocks_y,
                                                                    sim_param.block_dim, sim_param.road_width,
                                                                    sim_param.buildings_constant)

    # Finds number of each buildings
    num_med = sim_param.num_medical_buildings
    num_travel = sim_param.num_travel_buildings

    remaining_buildings = len(building_rects) - (num_med + num_travel)

    sum_ratios = sim_param.residential_ratio + sim_param.industrial_ratio + sim_param.commercial_ratio

    num_residential = int((sim_param.residential_ratio / sum_ratios) * remaining_buildings)
    num_commercial = int((sim_param.commercial_ratio / sum_ratios) * remaining_buildings)
    num_industrial = int((sim_param.industrial_ratio / sum_ratios) * remaining_buildings)

    # Ensures it all adds up
    num_residential += remaining_buildings - num_industrial - num_commercial - num_residential
    assert (num_residential + num_industrial + num_commercial + num_med + num_travel) == len(building_rects)

    # Puts values in list such that indexes match enum values in Building.Types
    nums = [num_med, num_commercial, num_travel, num_residential, num_industrial]

    # Loops through shuffled building indexes
    for i in (lambda a: (random.shuffle(a), a)[1])(list(range(len(building_rects)))):
        # Chooses type index and subtracts from that count
        index = random.choice([i for i in range(len(nums)) if nums[i] != 0])
        nums[index] -= 1

        # Randomizes floors
        if random.randint(1, 100) <= sim_param.high_rise_percentage:
            floors = random.randint(5, 40)
        else:
            floors = random.randint(1, 4)

        # Adds building
        buildings.add(Building(sim_manager, building_rects[i], midpoint(random.choice(building_rects[i].get_sides())),
                               Building.Types(index), floors))

    return buildings, smallest_road_width
