import pygame
import logging
from sim_manager import GraphicsData
from sim_renderer import SimRenderer
from enum import IntEnum
from typing import Optional
from app_sim_comms import AppSimComms
from my_pygame_components.typefield import TypeField
from my_pygame_components.button import Button
pygame.init()


class App(SimRenderer):
    """
    Overhead App manager, manages app state, manages GUI displays and visuals
    """
    # Window size relative to smaller screen resolution dimension (usually height)
    SCREEN_SIZE_CONSTANT = 0.8

    # App state enum
    class AppState(IntEnum):
        MAIN = 0
        SIM = 1

    def __init__(self):
        SimRenderer.__init__(self)

        # App while loop control flag
        self.__is_running = True

        # User screen dimensions, and app window dimensions
        self.SCREEN_DIMS = (pygame.display.Info().current_w,
                            pygame.display.Info().current_h)
        self.WINDOW_DIMS = (int(min(self.SCREEN_DIMS) * 0.8),) * 2
        logging.info("Window dims are " + str(self.WINDOW_DIMS))

        # App window and tick clock
        self.__window = pygame.display.set_mode(self.WINDOW_DIMS)
        self.__clock = pygame.time.Clock()
        # Event queue gotten from pygame each frame
        self.__events = []

        # Class responsible for managing and communicating with the sim process
        self.__sim_communicator = AppSimComms(self)

        # Class responsible for storing draw info of sim objects
        self.__graphics_data = GraphicsData()

    def start(self):
        self.run_app()

    def stop(self):
        self.__is_running = False

    def run_app(self):
        logging.info("App Started")

        while self.__is_running:
            # Clears screen
            self.__window.fill((50, 50, 50))

            # Stores events, captures quit event
            self.__events = pygame.event.get()
            for event in self.__events:
                if event.type == pygame.QUIT:
                    self.stop()

            # Updates display and ticks clock
            pygame.display.update()
            self.__clock.tick(60)
            pygame.display.set_caption("CovSim    FPS: " + str(self.__clock.get_fps()))

            # Grabs frame update from communicator and updates graphics data object
            # TODO: Move this into individual sim draw func once those are created
            frame_info = self.__sim_communicator.get_latest_frame_info()

            if frame_info is not None:
                if GraphicsData.Types(frame_info["type"]) == GraphicsData.Types.STATIC:
                    self.__graphics_data.buildings = frame_info["buildings"]
                    self.__graphics_data.objects = frame_info["objects"]

                elif GraphicsData.Types(frame_info["type"]) == GraphicsData.Types.DYNAMIC:
                    self.__graphics_data.people = frame_info["people"]

        logging.info("App Ended")




