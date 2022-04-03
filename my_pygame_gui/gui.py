"""Pygame GUI Package: GUI Manager

Module Description
==================
This module contains the main GUI manager class. Inherit from this to start
building an app using this GUI framework.

Copyright and Usage Information
===============================

This file pertains to the CovSim simulation software. The code inside
this file may be viewed by CSC faculty at University of Toronto. Otherwise,
this code is only to be used by running the program. Distributing or
using this code in any other way is prohibited.

This file is Copyright (c) 2021 Aleksey Panas, Rohit Shetty.
"""
import pygame
from my_pygame_gui.component import WindowComponent, Container
from my_pygame_gui.component_properties import Property, NumericProperty
import logging


class Gui:
    """Runs the GUI by calling the component tree"""
    # Window size relative to smaller screen resolution dimension (usually height)
    SCREEN_SIZE_CONSTANT = 0.8

    def __init__(self):
        # User screen dimensions, and app window dimensions
        self.SCREEN_DIMS = (pygame.display.Info().current_w,
                            pygame.display.Info().current_h)
        self.WINDOW_DIMS = (int(min(self.SCREEN_DIMS) * Gui.SCREEN_SIZE_CONSTANT),) * 2
        logging.info("Window dims are " + str(self.WINDOW_DIMS))

        # Pygame tick clock
        self._clock = pygame.time.Clock()

        # Window GUI component
        self._window = WindowComponent(self.WINDOW_DIMS[0], self.WINDOW_DIMS[1],
                                       background_color=(100, 100, 100))

        self._is_running = True
        # Event queue gotten from pygame each frame
        self._events = []

    def start(self):
        self.run_app()

    def stop(self):
        self._is_running = False

    def initialize(self):
        """Called before app GUI loop starts"""
        raise NotImplementedError

    def end(self):
        """Called right after GUI loop stops"""
        raise NotImplementedError

    def update(self):
        """Called every GUI loop iteration"""
        raise NotImplementedError

    def run_app(self):
        logging.info("App Started")

        # Calls initialize Method
        self.initialize()

        while self._is_running:
            # Stores events, captures quit event
            self._events = pygame.event.get()
            for event in self._events:
                if event.type == pygame.QUIT:
                    self.stop()

            # Calls update method
            self.update()

            # Renders GUI tree and handles events starting from window
            self._window.handle_component(self._events)

            # Updates display and ticks clock
            pygame.display.update()
            self._clock.tick(200)
            pygame.display.set_caption("CovSim    FPS: " + str(self._clock.get_fps()))

        # Calls end method
        self.end()

        logging.info("App Ended")
