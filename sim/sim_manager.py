from __future__ import annotations
from enum import IntEnum
import random
from sim.sim_components import *
from sim.city_generator import *
from dataclasses import dataclass
from geometry.geometry import Point, Rectangle


@dataclass
class SimParams:
    """Parameters for simulation

    Instance Attributes:
        - block_dim: the width and height of a city block
    """
    city_blocks_x: int
    city_blocks_y: int
    block_dim: float  # Measures in sim world distance units (DU), where (10 DU = 1 meter)
    buildings_constant: int  # A larger value increases building density per block
    road_width: float

    high_rise_percentage: float  # Number of buildings which have many floors

    num_medical_buildings: int
    num_travel_buildings: int

    # Summed up and converted into percentages:
    residential_ratio: float
    commercial_ratio: float
    industrial_ratio: float

    population: int
    avg_age: int
    mask_wearing_percentage: float
    average_travels_per_year: int
    is_closed_border: bool
    initial_vaccination_percentage: float
    vaccination_tendency: float  # TODO: Exact measure TBD
    is_vaccine_available: bool
    social_distancing: float  # TODO: Exact measure TBD
    homelessness_percentage: float


# Keeps track of graphics data
class GraphicsData:

    class Types(IntEnum):
        STATIC = 0
        DYNAMIC = 1
        BOTH = 2
    """
    Attributes:
        - buildings: List of building locations (id, top, left, width, height)
        - people: List of people info (id, is_infected, x, y) potentially more later
        - objects: List of interactables, (id, top, left, width, height)
    """
    def __init__(self):
        self.buildings: list[tuple[int, int, int, int, int]] = []
        self.people: list[tuple[int, bool, int, int]] = []
        self.objects: list[tuple[int, int, int, int, int]] = []
    
    def get_dynamic_sendable_info(self):
        return {"type": GraphicsData.Types.DYNAMIC.value,
                "people": self.people}

    def get_static_sendable_info(self):
        return {"type": GraphicsData.Types.STATIC.value,
                "buildings": self.buildings,
                "objects": self.objects}

    def get_all_sendable_info(self):
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
        self.city = City(self, generate_city_buildings(sim_params), )

    def progress_simulation(self, time_delta_ms: int) -> dict:
        """
        Progress the simulation world by the provided time_delta_ms in simulation
        world time measurement

        Preconditions:
            - time_delta_ms > 0
        """
        return self.__graphics_data.get_dynamic_sendable_info()

    def get_static_graphics_data(self) -> dict:
        """
        Return info on static simulation objects such as buildings and interactables
        """
        return self.__graphics_data.get_static_sendable_info()
