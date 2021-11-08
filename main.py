"""
Main file where the program will start

class App:
    Overhead manager for the app window and app navigation
    - Contains user's screen info
    - Contains pygame window
    - Runs main menu navigation including sim creation form

class Sim:
    Manager for the simulation
    - Contains city instance
    - Contains people instances
    - Contains main loop for running sim
    - Runs pygame and all events
    - Potentially has a computational thread to update the sim based on speed rate
    - Keeps track of and saves sim data

class SimRenderer:
    Takes in info from sim and renders frame

class Camera:
    Dataclass to store cam info

class Person:
    Person info
    - Contains personality traits
    - Contains age, gender, and other characteristics
    - Stores and manages decision info
    - Contains infection info
    - Stores location info

class City:
    City Info
    - Contains city grid dimensions
    - Contains buildings instances
    - Contains methods to be used by Person class for navigation (ie travel_to(target, current_loc))

class Building
    Building info
    - Contains grid coordinate of building
    - Contains building characteristics info

"""

import Sim

Sim.SimManager().start()

