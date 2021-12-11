from dataclasses import dataclass
from typing import Optional
from enum import IntEnum
from geometry.geometry import Rectangle


class Person:
    def __init__(self, sim):
        # Parent sim manager object
        self.sim = sim

        self.location = Location(0, 0)
        self.is_infected = False


class Building:
    """

    Instance Attributes
        - num_floors: more floors means less chance of infection with more people
        - rect: building world dimensions and location via DU measurements (10 DU = 1 meter)
        - purpose: purpose of the building
    """
    class Types(IntEnum):
        MEDICAL = 0  # Provides medical care (hospital)
        COMMERCIAL = 1  # Gives food and happiness (mall, restaurant)
        TRAVEL = 2  # Allows travel outside of city (airport)
        RESIDENTIAL = 3  # Can be assigned as someone's home (apartment building)
        INDUSTRIAL = 4  # Provides jobs, workplace (office complex, factory)

    def __init__(self, sim, rect: Rectangle, purpose: Types, floors: int):
        # Parent sim manager object
        self.sim = sim

        self.rect = rect

        self.num_floors = floors
        self.purpose = purpose


class City:
    def __init__(self, sim, buildings: set[Building], people: set[Person]):
        # Parent sim manager object
        self.sim = sim

        self.buildings = buildings
        self.people = people

    def path_find(self):
        pass

    def move(self, person, delta_x, delta_y):
        pass


@dataclass
class Location:
    """
    World-scale location for Person objects
    """
    x: float  # Relative to building topleft if inside building
    y: float  # Relative to building topleft if inside building
    building: Optional[Building] = None  # None if outside
