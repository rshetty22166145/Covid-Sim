import pygame
import logging
import datetime
from multiprocessing import Process, Pipe
from threading import Thread
from sim_manager import SimManager
from sim_renderer import SimRenderer
from typing import Optional
from my_queue import Queue

logging.basicConfig(filename='./logs/CovSim' +
                             str(datetime.datetime.now()) + '.log',
                    level=logging.DEBUG)


class App(SimRenderer):
    def __init__(self):
        SimRenderer.__init__(self)

        # App while loop control flag
        self.__running = True

        # User screen dimensions, and app window dimensions
        self.SCREEN_DIMS = (pygame.display.Info().current_w,
                            pygame.display.Info().current_h)
        self.WINDOW_DIMS = (500, 500)

        # App window and tick clock
        self.__window = pygame.display.set_mode(self.WINDOW_DIMS, pygame.SCALED)
        self.__clock = pygame.time.Clock()
        # Event queue gotten from pygame each frame
        self.__events = []

        # Class which runs the simulation
        self.__sim_manager: Optional[SimManager] = None
        # Connection between sim process and main app process
        self.__conn, child_conn = Pipe()
        # Process to run simulation
        self.__sim_process = Process(target=App.run_simulation_process,
                                     args=(self.__sim_manager, child_conn),
                                     daemon=True)
        # Stores events that happened in the sim
        self.__sim_events = Queue()
        # Stores an object containing sim object info to draw
        self.__current_frame_info = {}
        # Updated via receiver thread
        self.__latest_frame_info = {}

    def sim_receiver(self):
        while self.__running:
            try:
                events, frame_info = self.__conn.recv()
                for event in events:
                    self.__sim_events.enqueue(event)
            except:
                logging.error("Sim Manager sent data in an unexpected format.")

    @staticmethod
    def run_simulation_process(sim_manager, conn):
        # Data received from main process
        data_list = []

        # Adds any received data to data_list, thread to prevent locking up the sim
        def recv_data():
            while True:
                data_list.append(conn.recv())
        Thread(target=recv_data, daemon=True).start()

        while True:
            # Progresses sim and gets the output of the progression
            sim_output = sim_manager.progress_simulation(5)

    def start(self):
        self.run_app()

    def stop(self):
        self.__running = False

    def run_app(self):
        logging.info("App Started")

        while self.__running:
            self.__window.fill((50, 50, 50))

            self.__events = pygame.event.get()
            for event in self.__events:
                if event.type == pygame.QUIT:
                    self.__running = False

            self.__clock.tick()
            pygame.display.set_caption("CovSim    FPS: " + str(self.__clock.get_fps()))

        logging.info("App Ended")




