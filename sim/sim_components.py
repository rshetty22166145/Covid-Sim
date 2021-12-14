"""CovSim Sim Package: Sim Components

Module Description
==================
This module contains classes representing simulation objects

Copyright and Usage Information
===============================

This file pertains to the CovSim simulation software. The code inside
this file may be viewed by CSC faculty at University of Toronto. Otherwise,
this code is only to be used by running the program. Distributing or
using this code in any other way is prohibited.

This file is Copyright (c) 2021 Aleksey Panas, Rohit Shetty.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from enum import IntEnum
from geometry.geometry import *
from geometry.helpers import SECONDS_IN_YEAR
from geometry.path_finding import get_paths
from sim.sim_manager import *
import sim.models as models
import datetime
import random
import logging


class Person:
    """

    Instance Attributes:
        - location: location object to specify where person is
        - is_infected, is_vaccinated, is_homeless: duh
        - is_dead: Rest in peace homie
        - cause_of_death: It would suck to die of starvation
        - age: Age of person
        - mask_wearing_percentage: Each time this person enters or exits a building, this percentage is combined
        with the number of people in the area and a randomizer determines whether mask is on or off (percent 0 to 100)
        - travels_per_s: The chance that a person will decide to travel per second of sim time passed. Homeless
        people don't travel.
        - hunger: -100 is death of starvation, 0 is the start of immune system weakness, 20 is very hungry,
        50 is hungry, 100 is full, 120 is bloated
        - happiness: -150 is death by suicide, -50 is the start of depression and carelessness (less attention to
        covid prevention), 0 is sad, 50 is neutral, 100 is happy, 150 is ecstatic
        - temp: -100 is death from cold, 0 is the start of immune weakness, 50 is neutral, 100 is warm, 150 is hot
        - clothing: 0 is naked, 3 is summer wear, 10 is good winter gear
    """
    class CausesOfDeath(IntEnum):
        COVID = 0
        AGE = 1
        STARVATION = 2
        COLD = 3
        SUICIDE = 4

    def __init__(self, sim: SimManager, age: int, mask_wear_percent: int, is_vaccinated: bool, is_infected: bool,
                 is_homeless: bool, travels_per_year: int):
        # Parent sim manager object
        self.sim = sim

        self.is_infected = is_infected
        self.is_vaccinated = is_vaccinated
        self.is_homeless = is_homeless
        self.was_infected = is_infected

        self.is_dead = False
        self.cause_of_death = None

        self.age = age
        self.mask_wearing_percentage = mask_wear_percent
        self.travels_per_s = travels_per_year / SECONDS_IN_YEAR

        self._hunger = random.randint(50, 100)
        self.happiness = random.randint(0, 100)
        self._temp = 50
        self.clothing = 10

        self.is_male = random.choice((True, False))

        self.speed_DU_s = random.randint(50, 80) / 10

        # All attributes below are generated after initialization
        self.location: Optional[Location] = None

        self.home: Optional[Building] = None
        self.work: Optional[Building] = None

        # TODO: Implement people action queue

        # All attributes below are used to track decision-making
        self.last_movement: Optional[Path] = None
        self.current_path: Optional[Path] = None

    def act(self, time_delta_s) -> None:
        """Run the person's core action/decision-making process over the given time delta"""

    def finalize(self, location) -> None:
        """Assigns attributes that have not been assigned upon initialization"""
        self.location = location
        self.current_path, is_endpt_blocked = self.sim.city.path_find(self.location.point,
                                                                      self.sim.city.get_random_building().entrance_point)

    def change_hunger(self, hunger_delta: float) -> None:
        """Change hunger and execute consequences, if any"""
        self._hunger += hunger_delta
        # Need... food.... *dying noises*
        if self._hunger <= -100:
            self.is_dead = True
            self.cause_of_death = Person.CausesOfDeath.STARVATION
            logging.info("Person has died of starvation")
        self._hunger = min(self._hunger, 120)

    def change_temperature(self, temp_delta: float) -> None:
        """Change temperature and execute consequences, if any"""
        self._temp += temp_delta
        # Brrrrr....
        if self._temp <= -100:
            self.is_dead = True
            self.cause_of_death = Person.CausesOfDeath.COLD
            logging.info("Person has died of cold")
        self._temp = min(self._hunger, 150)

    def get_temperature(self):
        """Return person's temperature"""
        return self._temp

    def __str__(self):
        return "Person" + str({
            "is_infected": self.is_infected,
            "is_vaccinated": self.is_vaccinated,
            "is_homeless": self.is_homeless,
            "age": self.age,
            "mask_wearing": self.mask_wearing_percentage
        })

    def __repr__(self):
        return self.__str__()


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

    def __init__(self, sim: SimManager, rect: Rectangle, entrance_point: Point, purpose: Types, floors: int):
        # Parent sim manager object
        self.sim = sim

        self.rect = rect
        self.entrance_point = entrance_point

        self.num_floors = floors
        self.purpose = purpose


class City:
    """

    Instance Attributes:
        - buildings, people: lists of buildings and people in the simulation
        - smallest_road_width: width of the narrowest distance between buildings in the city
        - is_border_closed: prevents travel
        - is_vaccine_available: allows vaccination
        - time_s: total time passed since sim started.
        - date_time: tracks date and time in sim
    """
    class Seasons(IntEnum):
        SPRING = 0
        SUMMER = 1
        FALL = 2
        WINTER = 3

    def __init__(self, sim, buildings: set[Building], people: set[Person], smallest_road_width: float,
                 is_border_closed: bool, is_vaccine_available: bool):
        # Parent sim manager object
        self.sim = sim

        self.buildings = buildings
        self.people = people

        self.smallest_road_width = smallest_road_width
        self.is_border_closed = is_border_closed
        self.is_vaccine_available = is_vaccine_available

        self.time_s = 0
        self.date_time = datetime.datetime(year=2021, month=1, day=1, hour=9, minute=0, second=0)

    def progress_time(self, time_delta_s: int):
        """
        Move the simulation time ahead by time_delta_s

        Preconditions:
            - time_delta_s > 0
        """
        # Moves time forward
        self.time_s += time_delta_s
        self.date_time += datetime.timedelta(seconds=time_delta_s)

        # Activates people's brain cells, and makes them realize cold and hunger mwahahaha
        for p in self.people:
            # The gods have been merciful, world hunger is temporarily solved
            # p.change_hunger(models.hunger_change_per_second())
            p.change_temperature(models.temperature_change_per_second(self.get_season(),
                                                                      p.get_temperature(),
                                                                      p.clothing))
            p.act(time_delta_s)

    def finalize_people(self):
        """Generates the remaining attributes of people"""
        for p in self.people:
            p.finalize(self.get_random_free_location())

    def path_find(self, start: Point, end: Point) -> Optional[tuple[Path, bool]]:
        """Evaluates a random path and returns it along with whether the endpoint was blocked by a shape"""
        paths, was_endpoint_blocked = get_paths([b.rect for b in self.buildings], Vector(start, end),
                                                self.smallest_road_width / 4, max_paths=10, is_random=True)
        if len(paths) != 0:
            return paths[0], was_endpoint_blocked

    def move(self, person: Person, delta_x: float, delta_y: float) -> bool:
        """Mutate person's position if possible and return success. This method ensures that no illegal
        movement is done, and prevents any such movement (like moving through walls)"""
        # Can't move inside buildings
        if person.location.point is None:
            return False

        # Gets vector representing current location and end point location
        motion_vector = Vector(person.location.point, person.location.point + Point(delta_x, delta_y))

        # Checks if vector intersects any buildings
        if not any(s.rect.is_vector_intersect(motion_vector) for s in self.buildings):
            # Performs motion
            person.location.point += Point(delta_x, delta_y)
            return True
        return False

    def get_random_free_location(self, player_radius=5) -> Location:
        """Return a location within the city bounding box that doesn't collide with any buildings"""
        bound = self.get_bounding_box()

        # Do-while loop lads
        while True:
            pt = Point(random.randint(int(bound.left), int(bound.left + bound.width)),
                       random.randint(int(bound.top), int(bound.top + bound.height)))
            if not any([b.rect.get_inflated(player_radius).is_point_inside(pt) for b in self.buildings]):
                break
        return Location(point=pt)

    def get_bounding_box(self) -> Rectangle:
        """Return rectangle representing the city bounds, which are defined by
        the farthest building in each direction"""
        left = None
        right = None
        top = None
        bottom = None
        for b in self.buildings:
            if left is None or b.rect.left < left:
                left = b.rect.left
            if right is None or b.rect.left + b.rect.width > right:
                right = b.rect.left + b.rect.width
            if top is None or b.rect.top < top:
                top = b.rect.top
            if bottom is None or b.rect.top + b.rect.height > bottom:
                bottom = b.rect.top + b.rect.height
        return Rectangle(left=left, top=top,
                         width=right - left, height=bottom - top)

    def get_season(self) -> City.Seasons:
        """Gets current season. Seasons may affect immunity"""
        return City.Seasons(int(((self.date_time.month-3) % 12) // 3))

    def get_random_building(self) -> Building:
        """Return a random building from buildings"""
        return random.choice(list(self.buildings))

    def get_random_person(self) -> Person:
        """Return a random person from people"""
        return random.choice(list(self.people))


@dataclass
class Location:
    """
    World-scale location for Person objects.

    Instance Attributes:
        - point: coordinate location outside
        - building: inside this building, no specific coordinates

    Representation Invariants:
        - point is not None or building is not None
    """
    point: Optional[Point] = None  # Ignored if in building
    building: Optional[Building] = None  # None if outside
