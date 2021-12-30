"""Main Module

Module Description
==================
This module is used to run the app

Copyright and Usage Information
===============================

This file pertains to the CovSim simulation software. The code inside
this file may be viewed by CSC faculty at University of Toronto. Otherwise,
this code is only to be used by running the program. Distributing or
using this code in any other way is prohibited.

This file is Copyright (c) 2021 Aleksey Panas, Rohit Shetty.
"""
from plotting.comparisons import comparison_graph
from sync_app import SyncApp
import go as g
import logging
import datetime

import pygame


def csv_callback(file1_values: dict[float, float], file2_values: dict[float, float]):
    """Called by GUI to output graph comparison visual"""
    #raise InvalidColumnsError("Sample error message!")
    # print("FILE 1: ", file1_values, "\r\nFILE 2: ", file2_values, "\r\n")

    if file1_values is not None and len(file1_values) > 0:
        comparison_graph(file1_values, "./datasets/Toronto_data.csv")
    else:
        raise g.InvalidColumnsError("Cannot plot empty values")


def simulation_callback(params: dict) -> None:
    """Called by GUI to launch simulation"""

    #print (params)
    #return

    pygame.init()

    # Create App
    app = SyncApp(params)

    # Start app
    app.start()


logging.basicConfig(filename='./logs/CovSim' +
                             str(datetime.datetime.now().date()) + '.log',
                    level=logging.DEBUG)

logging.info("----------------------------")

if __name__ == "__main__":
    g.start_gui(csv_callback, simulation_callback)

    # simulation_callback({
    #     "city_blocks_x": 4,
    #     "city_blocks_y": 4,
    #     "block_dim": 150,
    #     "buildings_constant": 100,
    #     "road_width": 40,
    #
    #     "high_rise_percentage": 30,
    #
    #     "num_medical_buildings": 1,
    #     "num_travel_buildings": 2,
    #
    #     "residential_ratio": 2,
    #     "commercial_ratio": 1,
    #     "industrial_ratio": 1,
    #
    #     "population": 50,
    #     "avg_age": 40,
    #     "mask_wearing_percentage": 30,
    #     "average_travels_per_year": 10,
    #     "is_closed_border": False,
    #     "initial_vaccination_percentage": 10,
    #     "initial_infection_percentage": 10,
    #     "is_vaccine_available": True,
    #     "homelessness_percentage": 5,
    #     "quarantine_tendency": -1,
    #     "vaccination_tendency": -1,
    #     "social_distancing": -1,
    #     "world_threat_level_local": -1,
    #     "world_threat_level_international": -1
    # })
