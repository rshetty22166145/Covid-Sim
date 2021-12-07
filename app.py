import pygame
import logging
from sim_manager import GraphicsData
from app_gui import AppGui
from enum import IntEnum
from typing import Optional
from app_sim_comms import AppSimComms
pygame.init()

# TODO: Adapt button component
# TODO: Add image component
# TODO: Adapt Typefield component
# TODO: Add main menu (New Sim, Load Sim, Compare Data, Quit)
# TODO: Add simple new sim screen
# TODO: Add sim canvas component
# TODO: Integrate sim process with canvas component somehow
# TODO: Test sim process extensively

# TODO: Implement transitions (with easing?)


class App(AppGui):
    """
    Overhead App manager, manages app state, manages GUI displays and visuals
    """

    def __init__(self):
        AppGui.__init__(self)

        # Class responsible for managing and communicating with the sim process
        self.__sim_communicator = AppSimComms(self)

        # Class responsible for storing draw info of sim objects
        self.__graphics_data = GraphicsData()

    def initialize(self):
        pass

    def end(self):
        pass

    def update(self):
        pass


# Grabs frame update from communicator and updates graphics data object
# # TODO: Move this into individual sim draw func once those are created
# frame_info = self.__sim_communicator.get_latest_frame_info()
#
# if frame_info is not None:
#     if GraphicsData.Types(frame_info["type"]) == GraphicsData.Types.STATIC:
#         self.__graphics_data.buildings = frame_info["buildings"]
#         self.__graphics_data.objects = frame_info["objects"]
#
#     elif GraphicsData.Types(frame_info["type"]) == GraphicsData.Types.DYNAMIC:
#         self.__graphics_data.people = frame_info["people"]



