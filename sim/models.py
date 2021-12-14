"""CovSim Sim Package: Probability Models

Module Description
==================
This module contains all the probability models related to the simulation. All models are
subject to change as testing is done and simulation accuracy is compared to real data

Copyright and Usage Information
===============================

This file pertains to the CovSim simulation software. The code inside
this file may be viewed by CSC faculty at University of Toronto. Otherwise,
this code is only to be used by running the program. Distributing or
using this code in any other way is prohibited.

This file is Copyright (c) 2021 Aleksey Panas, Rohit Shetty.
"""
from __future__ import annotations
import random
import math
from geometry.helpers import *
from geometry.geometry import *
from sim.sim_components import *


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


def hunger_change_per_second() -> float:
    """Gives the hunger change per second for a person"""
    return -0.0023


def temperature_change_per_second(season: int, cur_temp: float, clothing: float) -> float:
    """Return the temperature change per second for a person with a current temperature value of
    cur_temp and a clothing value of clothing, with the given season"""
    def clothing_multiplier_mult(clothing_value: float) -> float:
        return (-0.95 / 15) * clothing_value + 1

    def clothing_multiplier_add(clothing_value: float) -> float:
        return clothing_value / 150

    def summer(temp: float) -> float:
        return (0.0104 * (0.97545 ** (temp-85)) + 0.005) * \
               clothing_multiplier_mult(clothing)

    def winter(temp: float) -> float:
        return -summer(50 - temp)

    def fall(temp: float) -> float:
        return winter(temp) * 0.5

    def spring(temp: float) -> float:
        return summer(temp) * 0.5

    return {1: summer,
            0: spring,
            2: fall,
            3: winter}[season](cur_temp) + clothing_multiplier_add(clothing)


def probability_infection_per_sec_at_distance(distance: float, healthy_hunger: float, healthy_temp: float,
                                              is_mask_healthy: bool, is_mask_infected: bool,
                                              was_previously_infected_healthy: bool,
                                              is_vaccinated_healthy: bool):
    """Given the distance between and healthy and infected person, and certain
    information about the health and infected, return the probability that the health
    person was infected after spending 1 second under those parameters"""
    # Evaluates base model probability from distance
    prob_from_distance = max(min(.225 * 2 ** (-distance), 1), 0)

    # Calculates hunger and cold multipliers
    hunger_mult = max((-1 / 300) * healthy_hunger + 1, 1)
    cold_mult = max((-1 / 300) * healthy_temp + 1, 1)

    # Applies cold and hunger multipliers
    prob_from_distance *= hunger_mult * cold_mult

    # Applies mask wearing multipliers
    prob_from_distance *= (0.5 if is_mask_infected else 1) * (0.5 if is_mask_healthy else 1)

    # Applies vaccination and reinfection multipliers
    prob_from_distance *= (0.01 if is_vaccinated_healthy else 1) * (0.05 if was_previously_infected_healthy else 1)

    return prob_from_distance


def scale_probability(pc: float, sc: float, sn: float, accuracy=3) -> float:
    """Given a probability of pc, which is the probability of an event occurring
    within a time interval of sc seconds, return the probability of the event
    occurring within a time interval of sn"""
    return round(1-(1-pc)**(sn/sc), accuracy)


def probability_infected_from_paths(path1: Path, path2: Path, delta_time_s: float,
                                    healthy_hunger: float, healthy_temp: float,
                                    is_mask_healthy: bool, is_mask_infected: bool,
                                    was_previously_infected_healthy: bool,
                                    is_vaccinated_healthy: bool
                                    ) -> float:
    """
    Given 2 paths which represent the movement of 2 people over a delta time, assuming
    one is infected and one is not, return the probability that the healthy person got
    infected using the distance model.
    """

    distances = [sum(dist(v.start, v.end) for v in path1.get_vectors()),
                 sum(dist(v.start, v.end) for v in path2.get_vectors())]

    speeds = [d / delta_time_s for d in distances]
    print(speeds)

    times_1 = []
    times_2 = []

    # find critical times based on speed.
    p1_vecs = path1.get_vectors()
    p2_vecs = path2.get_vectors()

    for i in range(1, len(p1_vecs)):
        times_1.append(sum((dist(v.start, v.end) / speeds[0]) for v in p1_vecs[:i]))

    for j in range(1, len(p2_vecs)):
        times_2.append(sum((dist(v.start, v.end) / speeds[1]) for v in p2_vecs[:j]))

    times_1 += [delta_time_s]
    times_2 += [delta_time_s]

    times = sorted(list(set(times_1 + times_2)))

    # Tracks previous position where left off
    st_pos_1 = path1.points[0]
    st_pos_2 = path2.points[0]
    vecs_1 = []
    vecs_2 = []
    new_times = []
    time_sum = 0
    for crit_time in times:
        # works with 1st person
        if crit_time in times_1:
            next_pt = path1.points[times_1.index(crit_time) + 1]
        else:
            closest_path_pt = path1.points[times_1.index([t for t in times_1 if t >= crit_time][0]) + 1]
            hyp_long = dist(closest_path_pt, st_pos_1)
            hyp_short = (crit_time - time_sum) * speeds[0]

            a = closest_path_pt[0] - st_pos_1[0]
            b = closest_path_pt[1] - st_pos_1[1]

            next_pt = Point(st_pos_1[0] + (hyp_short / hyp_long) * a,
                            st_pos_1[1] + (hyp_short / hyp_long) * b)

        vecs_1.append(Vector(Point(st_pos_1.x, st_pos_1.y), Point(next_pt.x, next_pt.y)))
        st_pos_1 = next_pt

        # works with 2nd person
        if crit_time in times_2:
            next_pt = path2.points[times_2.index(crit_time) + 1]
        else:
            closest_path_pt = path2.points[times_2.index([t for t in times_2 if t >= crit_time][0]) + 1]
            hyp_long = dist(closest_path_pt, st_pos_2)
            hyp_short = (crit_time - time_sum) * speeds[1]

            a = closest_path_pt[0] - st_pos_2[0]
            b = closest_path_pt[1] - st_pos_2[1]

            next_pt = Point(st_pos_2[0] + (hyp_short / hyp_long) * a,
                            st_pos_2[1] + (hyp_short / hyp_long) * b)

        vecs_2.append(Vector(Point(st_pos_2.x, st_pos_2.y), Point(next_pt.x, next_pt.y)))
        st_pos_2 = next_pt

        new_times.append(crit_time - time_sum)

        time_sum = crit_time

    # Find the probabilities of infection for each vector pair
    probabilities = [probability_infected_from_vectors(vecs_1[i], vecs_2[i], new_times[i],
                                                       healthy_hunger, healthy_temp,
                                                       is_mask_healthy, is_mask_infected,
                                                       was_previously_infected_healthy,
                                                       is_vaccinated_healthy) for i in range(len(vecs_1))]
    # in a list of probs, the chance of the event occurring is 1-(chance of event not occurring in all probs)
    return 1 - math.prod([1 - prob for prob in probabilities])


def probability_infected_from_vectors(v1: Vector, v2: Vector, delta_time_s: float,
                                      healthy_hunger: float, healthy_temp: float,
                                      is_mask_healthy: bool, is_mask_infected: bool,
                                      was_previously_infected_healthy: bool,
                                      is_vaccinated_healthy: bool,
                                      trapezoidal_intervals_per_sec=10) -> float:
    """
    Given 2 vectors which represent the movement of 2 people over a delta time, assuming
    one is infected and one is not, return the probability that the healthy person got
    infected using the distance model.

    trapezoidal_intervals_per_sec is used to specify how many intervals to use in integral
    approximation when finding distance function average, for each second of time delta
    """
    # Distance function between vectors over time, where d(0) is the distance between vector
    # starting points and d(delta_time_s) is the distance between their endpoints
    d = distance_func_between_vectors(v1, v2, delta_time_s)

    # Find average distance between vectors on the time interval
    average_dist = approximated_function_average_on_interval(int(round(trapezoidal_intervals_per_sec * delta_time_s)),
                                                             0, delta_time_s, d)

    return scale_probability(
        probability_infection_per_sec_at_distance(average_dist, healthy_hunger, healthy_temp, is_mask_healthy,
                                                  is_mask_infected, was_previously_infected_healthy,
                                                  is_vaccinated_healthy), 1, delta_time_s)
