"""CovSim Sim Package: Sim Manager

Module Description
==================
This module contains the overhead manager class to run the simulation, along with two
dataclasses representing graphical data output from the simulation, as well as the
simulation input parameters to configure the sim.

Copyright and Usage Information
===============================

This file pertains to the CovSim simulation software. The code inside
this file may be viewed by CSC faculty at University of Toronto. Otherwise,
this code is only to be used by running the program. Distributing or
using this code in any other way is prohibited.

This file is Copyright (c) 2021 Aleksey Panas, Rohit Shetty.
"""
from __future__ import annotations
from enum import IntEnum
import random
import sim.sim_components as sc
import sim.city_generator as city_gen
from dataclasses import dataclass
from geometry.geometry import Point, Rectangle
import csv
from os.path import exists


def write_to_csv(filename: str, row: list) -> None:
    """Adds a row to a specified csv file. File name is the name of the csv, without .csv,
    and without a path. The path will be automatically set to simdata folder"""
    # open the file in the write mode
    is_exist = True
    if not exists('../simdata/' + filename + '.csv'):
        is_exist = False

    f = open('../simdata/' + filename + '.csv', 'w')

    # create the csv writer
    writer = csv.writer(f)

    # Adds headers if new file
    if not is_exist:
        writer.writerow(['day_number', 'population', 'cases_since_last'])

    # write a row to the csv file
    writer.writerow(row)

    # close the file
    f.close()


@dataclass
class SimParams:
    """Parameters for simulation. Any distance or world size measurements should be
    considered in terms of world distance units, DU, where 5 DU = 1 meter.

    Instance Attributes:
        - city_blocks_x, city_blocks_y: dimensions of city in blocks, where each block can contain many buildings
        - block_dim: the width and height of a city block
        - buildings_constant: An arbitrary value which influences the final number of buildings in the city, the higher
        it is, the more buildings
        - road_width: Space between city blocks. Local spacing within each block is derived from this value
        - high_rise_percentage: The chance for each building to have 5+ floors
        - residential_ratio, commercial_ratio, industrial_ratio: summed up and converted into proportions. After
        subtracting the travel and medical buildings, the remaining buildings split by these proportions.
        - avg_age: The average age of the population
        - mask_wearing_percentage: Each person has their own percentage for mask wearing, which determines how often
        they wear a mask. This value indicates what the average mask_wearing_percentage value should be (% 0-100)
        - average_travels_per_year: How many travels does a person make on average per year, used to randomize
        when a person decides to travel
        - is_closed_border: Prevents travel entirely
        - initial_vaccination_percentage: (% 0-100) how many people are initially vaccinated
        - initial_infection_percentage: (% 0-100) how many people are initially infected
        - is_vaccine_available: further vaccination impossible without vaccine
        - homelessness_percentage: how many people are homeless
        - quarantine_tendency:
        - vaccination_tendency:
        - social_distancing:
    """
    city_blocks_x: int
    city_blocks_y: int
    block_dim: float  # Measures in (DU)
    buildings_constant: int  # A larger value increases building density per block
    road_width: float

    high_rise_percentage: float  # Number of buildings which have many floors

    num_medical_buildings: int
    num_travel_buildings: int

    # Summed up and converted into percentages:
    residential_ratio: int
    commercial_ratio: int
    industrial_ratio: int

    population: int
    avg_age: int
    mask_wearing_percentage: int
    average_travels_per_year: int
    is_closed_border: bool
    initial_vaccination_percentage: float
    initial_infection_percentage: float
    is_vaccine_available: bool
    homelessness_percentage: float
    quarantine_tendency: float  # TODO: Exact measure TBD
    vaccination_tendency: float  # TODO: Exact measure TBD
    social_distancing: float  # TODO: Exact measure TBD
    world_threat_level_local: float  # TODO: Exact measure TBD
    world_threat_level_international: float  # TODO: Exact measure TBD


# Keeps track of graphics data
class GraphicsData:
    """
    Keeps track of sim data necessary to render sim-related graphics. The dictionaries
    outputted by the getter methods would be sent over the pipe between the graphics
    process and the sim process, but this was not fully implemented in time, so
    this class is unused

    Instance Attributes:
        - buildings: List of building locations (id, top, left, width, height)
        - people: List of people info (id, is_infected, x, y) potentially more later
        - objects: List of interactables, (id, top, left, width, height)
    """
    class Types(IntEnum):
        STATIC = 0
        DYNAMIC = 1
        BOTH = 2

    def __init__(self):
        self.buildings: list[tuple[int, int, int, int, int]] = []
        self.people: list[tuple[int, bool, int, int]] = []
        self.objects: list[tuple[int, int, int, int, int]] = []
    
    def get_dynamic_sendable_info(self) -> dict:
        return {"type": GraphicsData.Types.DYNAMIC.value,
                "people": self.people}

    def get_static_sendable_info(self) -> dict:
        return {"type": GraphicsData.Types.STATIC.value,
                "buildings": self.buildings,
                "objects": self.objects}

    def get_all_sendable_info(self) -> dict:
        return {"type": GraphicsData.Types.BOTH.value,
                "buildings": self.buildings,
                "objects": self.objects,
                "people": self.people}


class SimManager:
    """"""
    # Proportion of main road_width that local roads should be
    LOCAL_ROAD_MULTIPLIER = 0.5

    def __init__(self, sim_params: SimParams):
        self.__graphics_data = GraphicsData()

        # DEBUG: Creates arbitrary building, object, and people graphical data
        self.__graphics_data.buildings = [tuple(i for _ in range(5)) for i in range(10)]
        self.__graphics_data.objects = [tuple(i for _ in range(5)) for i in range(20, 30)]
        self.__graphics_data.people = [tuple(i for _ in range(5)) for i in range(40, 50)]

        # Generate city
        buildings, smallest_road = city_gen.generate_city_buildings(self, sim_params)
        people = city_gen.generate_city_people(self, sim_params)

        self.city = sc.City(self, buildings, people, smallest_road, sim_params.is_closed_border,
                            sim_params.is_vaccine_available)
        self.city.finalize_people()

        # Creates random value so files for each sim are unique
        self.sim_file_id = random.randint(10000, 99999)

    def progress_simulation(self, time_delta_s: int):  # -> dict:
        """
        Progress the simulation world by the provided time_delta_s in simulation
        world time measurement

        Preconditions:
            - time_delta_s > 0
        """
        # Progresses simulation
        self.city.progress_time(time_delta_s)

        # Records csv data
        write_to_csv('sim' + str(self.sim_file_id), [])

        # return self.__graphics_data.get_dynamic_sendable_info()

    def get_static_graphics_data(self) -> dict:
        """
        Return info on static simulation objects such as buildings and interactables
        """
        return self.__graphics_data.get_static_sendable_info()
