"""CovSim Sim Module: Probability Models

Module Description
==================
This module contains probability functions used by the simulation to roll chance
on events,

Copyright and Usage Information
===============================

This file pertains to the CovSim simulation software. The code inside
this file may be viewed by CSC faculty at University of Toronto. Otherwise,
this code is only to be used by running the program. Distributing or
using this code in any other way is prohibited.

This file is Copyright (c) 2021 Aleksey Panas, Rohit Shetty.
"""
import random
import math
from geometry.helpers import average


def roll_probability(prob: float) -> bool:
    """
    Roll the probability and return whether it was successful

    Preconditions:
        - 0 <= prob <= 1
    """
    total = 1
    while prob != int(prob):
        total *= 10
        prob *= 10
    return random.randint(1, total) <= prob


n = 100000
rolls = 5
results = []
for _ in range(n):
    results.append(sum([roll_probability(0.2) for _ in range(rolls)]) == 2)
print(average(results))

