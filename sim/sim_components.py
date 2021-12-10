from dataclasses import dataclass
from typing import Optional
from enum import IntEnum


class Person:
    def __init__(self, sim):
        # Parent sim manager object
        self.sim = sim

        self.location = Location(0, 0)
        self.is_infected = False


class Building:
    class Types(IntEnum):
        MEDICAL = 0
        FOOD = 1
        TRAVEL = 2
        HOME = 3
        WORK = 4

    def __init__(self, sim, purpose: Types):
        # Parent sim manager object
        self.sim = sim

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
