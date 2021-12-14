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
from app import App
import logging
import datetime

logging.basicConfig(filename='./logs/CovSim' +
                             str(datetime.datetime.now().date()) + '.log',
                    level=logging.DEBUG)

logging.info("----------------------------")

if __name__ == "__main__":
    # Create App
    app = App()

    # Start app
    app.start()
