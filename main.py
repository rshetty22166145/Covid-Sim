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
from sync_app import SyncApp
import guizero_gui.go as g
import logging
import datetime


def csv_callback(keys1, vals1, keys2, vals2):
    """Called by GUI to output graph comparison visual"""
    #raise InvalidColumnsError("Sample error message!")
    print("KEYS 1: ", keys1, "\r\nVALUES 1: ", vals1, "\r\n", "KEYS 2: ", keys2, "\r\nVALUES 2: ", vals2, "\r\n")


def simulation_callback(params: dict) -> None:
    """Called by GUI to launch simulation"""
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
