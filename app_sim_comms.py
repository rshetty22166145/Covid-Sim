import pygame
import logging
from multiprocessing import Process, Pipe
from threading import Thread, Lock
from sim.sim_manager import SimManager
from typing import Optional
from my_queue import Queue
import copy


class AppSimComms:
    """
    In charge of communicating with Sim process and
    maintaining graphical info that it sends
    """
    def __init__(self, app):
        self._sim_process: Optional[Process] = None
        # Connection between sim process and main app process
        self._conn = None

        # Stores events that happened in the sim
        self._sim_events = Queue()
        # Updated via receiver thread
        self._latest_frame_info = None
        self._latest_frame_info_lock = Lock()

        # Parent app class
        self._app = app

    def get_latest_frame_info(self):
        with self._latest_frame_info_lock:
            f = self._latest_frame_info
        return f

    def get_next_sim_event(self):
        return self._sim_events.dequeue()

    def is_sim_queue_empty(self):
        return self._sim_events.is_empty()

    def start_simulation(self):
        if not self._sim_process.is_alive():
            # Creates duplex connection pair
            self._conn, child_conn = Pipe()

            # Creates and starts simulation process
            self._sim_process = Process(target=AppSimComms.run_simulation_process,
                                        args=(SimManager(), child_conn),
                                        daemon=True)
            self._sim_process.start()

            # Starts reception thread
            Thread(target=self.sim_receiver, daemon=True).start()

    def stop_simulation(self):
        if self._sim_process.is_alive():
            # Sends string to end process
            self._conn.send("END")

    def sim_receiver(self):
        while True:
            try:
                # Receives sim data
                events, frame_info = self._conn.recv()

                # Adds sim graphical events to queue
                for event in events:
                    self._sim_events.enqueue(event)

                # Sets latest frame with lock
                with self._latest_frame_info_lock:
                    self._latest_frame_info = frame_info
            except TypeError:
                logging.error("Sim Manager sent data in an unexpected format.")
            except (EOFError, OSError):
                # Occurs when simulation process closes its connection
                # Or if own connection is closed
                break

        self._conn.close()

    @staticmethod
    def run_simulation_process(sim_manager, conn):
        logging.info("Sim Process successfully started")

        # Data received from main process
        data_list = []
        # Send "END" string over pipe to end simulation process
        is_running = True

        # Receives data from main app on a separate thread
        def recv_data():
            nonlocal is_running

            while True:
                try:
                    data = conn.recv()
                except (EOFError, OSError):
                    # Ends this process if the main process closed the connection
                    # or if own connection is closed by main thread
                    is_running = False
                    break

                # Send "END" special string to end this process
                if data == "END":
                    is_running = False
                else:
                    data_list.append(conn.recv())
        Thread(target=recv_data, daemon=True).start()

        while is_running:
            # Progresses sim and gets the output of the progression
            events, frame_info = sim_manager.progress_simulation(5)
            conn.send(events, frame_info)

        # Closes connection
        conn.close()

        logging.info("Sim Process successfully finished")
