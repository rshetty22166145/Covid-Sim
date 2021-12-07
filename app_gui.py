import pygame
from my_pygame_components.component import WindowComponent, Container
from my_pygame_components.component_properties import Property, NumericProperty
import logging


class AppGui:
    """Runs the GUI by calling the component tree"""
    # Window size relative to smaller screen resolution dimension (usually height)
    SCREEN_SIZE_CONSTANT = 0.8

    def __init__(self):
        # User screen dimensions, and app window dimensions
        self.SCREEN_DIMS = (pygame.display.Info().current_w,
                            pygame.display.Info().current_h)
        self.WINDOW_DIMS = (int(min(self.SCREEN_DIMS) * 0.8),) * 2
        logging.info("Window dims are " + str(self.WINDOW_DIMS))

        # Pygame tick clock
        self.__clock = pygame.time.Clock()

        # Window GUI component
        self.__window = WindowComponent(pygame.display.set_mode(self.WINDOW_DIMS),
                                        self.WINDOW_DIMS[0], self.WINDOW_DIMS[1],
                                        background_color=(100, 100, 100))

        self.__is_running = True
        # Event queue gotten from pygame each frame
        self.__events = []

    def start(self):
        self.run_app()

    def stop(self):
        self.__is_running = False

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

        while self.__is_running:
            # Stores events, captures quit event
            self.__events = pygame.event.get()
            for event in self.__events:
                if event.type == pygame.QUIT:
                    self.stop()

            # Calls update method
            self.update()

            # Renders GUI tree and handles events starting from window
            self.__window.handle_component(self.__events)

            # Updates display and ticks clock
            pygame.display.update()
            self.__clock.tick(60)
            pygame.display.set_caption("CovSim    FPS: " + str(self.__clock.get_fps()))

        # Calls end method
        self.end()

        logging.info("App Ended")
