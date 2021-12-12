import pygame
import logging
import time
import math
from sim.sim_manager import GraphicsData
from app_gui import AppGui
from app_sim_comms import AppSimComms
from my_pygame_components.rectangle import RectangleComponent
from my_pygame_components.component_properties import Property, NumericProperty
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
        self._sim_communicator = AppSimComms(self)

        # Class responsible for storing draw info of sim objects
        self._graphics_data = GraphicsData()

        self.count = 0

    def initialize(self):
        self.vanishing_rect = RectangleComponent(
            width=NumericProperty(200),
            height=NumericProperty(50),
            top=NumericProperty(50),
            left=NumericProperty(50),
            color=Property((150, 150, 150)), hover_color=Property((150, 250, 150))
        )
        self.resizing_rect = RectangleComponent(
            width=NumericProperty(100),
            height=NumericProperty(100),
            top=NumericProperty(0.5, is_relative=True, relative_prop_name="height"),
            left=NumericProperty(0),
            color=Property((150, 150, 150)), hover_color=Property((150, 250, 150))
        )
        self._window.add_child(self.vanishing_rect)
        self._window.add_child(self.resizing_rect)

        self._window.add_child(RectangleComponent(
            width=NumericProperty(0.1, is_relative=True, relative_prop_name="width"),
            height=NumericProperty(0.5, is_relative=True, relative_prop_name="height"),
            top=NumericProperty(0.25, is_relative=True, relative_prop_name="height"),
            left=NumericProperty(0.45, is_relative=True, relative_prop_name="width"),
            color=Property((150, 100, 100)), hover_color=Property((180, 150, 150))
        ))

        for x in range(10):
            for y in range(10):
                self._window.add_child(RectangleComponent(
                    width=NumericProperty(20),
                    height=NumericProperty(20),
                    top=NumericProperty(20 + 30 * x),
                    left=NumericProperty(20 + 30 * y),
                    color=Property((150, 150, 150)), hover_color=Property((150, 250, 150))
                ))

    def end(self):
        pass

    def update(self):
        self.count += 1
        if self.count % 200 < 100:
            self.vanishing_rect.disable_component()
        else:
            self.vanishing_rect.enable_component()

        self.resizing_rect.update_property("width", 100 + math.sin(time.time()) * 20)


# Grabs frame update from communicator and updates graphics data object
# # TODO: Move this into individual sim draw func once those are created
# frame_info = self._sim_communicator.get_latest_frame_info()
#
# if frame_info is not None:
#     if GraphicsData.Types(frame_info["type"]) == GraphicsData.Types.STATIC:
#         self._graphics_data.buildings = frame_info["buildings"]
#         self._graphics_data.objects = frame_info["objects"]
#
#     elif GraphicsData.Types(frame_info["type"]) == GraphicsData.Types.DYNAMIC:
#         self._graphics_data.people = frame_info["people"]



