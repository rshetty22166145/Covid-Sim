from __future__ import annotations
import my_path_finding.geometry as g


def dist(p, q):
    return ((q[1] - p[1]) ** 2 + (q[0] - p[0]) ** 2) ** 0.5


def ccw(A: g.Point, B: g.Point, C: g.Point) -> bool:
    """Checks intersection of three points by cases"""
    return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)


def intersect_points(A: g.Point, B: g.Point, C: g.Point, D: g.Point) -> bool:
    """Checks Instersection of segment AB and CD"""
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def are_vectors_intersecting(vector1: g.Vector, vector2: g.Vector) -> bool:
    """Return whether vectors intersect"""
    return intersect_points(vector1.start, vector1.end, vector2.start, vector2.end) and \
        intersect_points(vector1.end, vector1.start, vector2.start, vector2.end) and \
        intersect_points(vector1.start, vector1.end, vector2.end, vector2.start) and \
        intersect_points(vector1.end, vector1.start, vector2.end, vector2.start)
