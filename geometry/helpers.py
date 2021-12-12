from __future__ import annotations
import geometry.geometry as g
from typing import Union
import random

SECONDS_IN_YEAR = 31536000


def dist(p, q):
    return ((q[1] - p[1]) ** 2 + (q[0] - p[0]) ** 2) ** 0.5


def ccw(A: g.Point, B: g.Point, C: g.Point) -> bool:
    """Checks intersection of three points by cases"""
    return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)


def midpoint(vector: g.Vector) -> g.Point:
    """Returns midpoint of vector"""
    return vector.start + ((vector.end - vector.start) / 2)


def intersect_points(A: g.Point, B: g.Point, C: g.Point, D: g.Point) -> bool:
    """Checks Instersection of segment AB and CD"""
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def are_vectors_intersecting(vector1: g.Vector, vector2: g.Vector) -> bool:
    """Return whether vectors intersect"""
    # Calling 4 times with shuffled parameters is necessary since the algorithm is
    # inconsistent depending on input order.
    return intersect_points(vector1.start, vector1.end, vector2.start, vector2.end) and \
        intersect_points(vector1.end, vector1.start, vector2.start, vector2.end) and \
        intersect_points(vector1.start, vector1.end, vector2.end, vector2.start) and \
        intersect_points(vector1.end, vector1.start, vector2.end, vector2.start)


def average(values: Union[list[int], tuple[int, ...], set[int]]):
    """Returns average, duh"""
    return sum(values) / len(values)


def generate_integers_with_average(lower_bound: int, upper_bound: int, avg: int, quantity: int) -> list[int]:
    """Generate quantity integers in a list within lower and upper bound inclusive such that
    the average of the integers is close or equal to avg"""
    assert lower_bound <= avg <= upper_bound

    # Generates ages between bounds
    bounds = (lower_bound, upper_bound)
    values = [random.randint(bounds[0], bounds[1]) for _ in range(quantity)]

    # If average is too high or too low, set the lambda while loop condition getter to tweak in appropriate direction
    eval_cond_and_id = ((lambda a: average(a) > avg), "down") \
        if average(values) > avg else \
        ((lambda a: average(a) < avg), "up")

    # Tweak ages in appropriate direction until the average crosses the specified avg value
    while eval_cond_and_id[0](values):
        tweakable_age_indexes = [i for i in range(len(values)) if values[i] not in bounds]
        if eval_cond_and_id[1] == "down":
            values[random.choice(tweakable_age_indexes)] -= 1
        else:
            values[random.choice(tweakable_age_indexes)] += 1

    return values


def get_shuffled(lst: list) -> list:
    """random.shuffle but returns a copy of the shuffled list"""
    lst = [e for e in lst]
    random.shuffle(lst)
    return lst
