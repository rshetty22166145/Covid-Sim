from dataclasses import dataclass
from typing import Optional
from enum import IntEnum


class Person:
    def __init__(self, sim):
        # Parent sim manager object
        self.sim = sim

        self.location = Location(0, 0)
        self.is_infected = False


class Interactable:
    """
    Types:
        - Medical
        - Food
        - Travel
        - Home
    """
    class Types(IntEnum):
        MEDICAL = 0
        FOOD = 1
        TRAVEL = 2
        HOME = 3

    def __init__(self, sim):
        # Parent sim manager object
        self.sim = sim

        # TODO: Interactables can store infection on them
        # TODO: Determine types of interactables


class Building:
    def __init__(self, sim, interactables: set[Interactable]):
        # Parent sim manager object
        self.sim = sim

        self.interactables = interactables


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
