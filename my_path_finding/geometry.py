from __future__ import annotations
import math
from my_path_finding.helpers import *
from typing import Any, Callable, Union, Optional
from my_path_finding.helpers import midpoint, dist


class Point:
    """
    Representation of a 2D point
    """
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def _perform_operation(self, other: Any,
                           operation: Callable[[float, Union[int, float]], float]):
        if isinstance(other, (float, int)):
            return Point(operation(self.x, other), operation(self.y, other))
        elif isinstance(other, (list, Point, tuple)) and len(other) == 2:
            return Point(operation(self.x, other[0]), operation(self.y, other[1]))
        else:
            raise TypeError("Can only add numerical values to points")

    def __add__(self, other: Any) -> Point:
        return self._perform_operation(other, lambda a, b: a + b)

    def __sub__(self, other: Any) -> Point:
        return self._perform_operation(other, lambda a, b: a - b)

    def __truediv__(self, other) -> Point:
        return self._perform_operation(other, lambda a, b: a / b)

    def __mul__(self, other) -> Point:
        return self._perform_operation(other, lambda a, b: a * b)

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise TypeError("Indexing into a point must be done with integers, not " + str(type(item).__name__))
        elif item not in (0, 1):
            raise IndexError("A point can only be indexed at 0 or 1")
        return self.x if item == 0 else self.y

    def __iter__(self):
        return (self.x, self.y).__iter__()

    def __str__(self):
        return "Point" + str(tuple(self))

    def __len__(self):
        return 2

    def __repr__(self):
        return self.__str__()


class Vector:
    """
    Representation of a 2D vector
    """
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def __iter__(self):
        return iter((self.start, self.end))

    def __str__(self):
        return "Vector" + str(tuple(self))

    def __repr__(self):
        return self.__str__()


class Path:
    """
    Representation of a path as a list of sequential points
    """
    def __init__(self, points: list[Point]):
        self.points = points

    def get_vectors(self) -> list[Vector]:
        """Return the path as a list of connected vectors. Point references are maintained
        in the resulting vector list!"""
        return [Vector(self.points[i], self.points[i + 1]) for i in range(len(self.points) - 1)]

    def __iter__(self):
        return iter(self.points)

    def __str__(self):
        return "Path" + str(tuple(self))

    def __repr__(self):
        return self.__str__()


class Shape:
    """
    Abstract class to define shapes for pathfinding purposes
    """
    def is_vector_intersect(self, vector: Vector) -> bool:
        """Return if the vector intersects the shape, exclusive of shape edges"""
        raise NotImplementedError

    def is_point_inside(self, point: Point):
        """Return if point is inside the shape. If point is on edges, does not count"""
        raise NotImplementedError

    def get_vertices(self, vector: Optional[Vector] = None) -> list[Point]:
        """Return significant points of the shape given a vector"""
        raise NotImplementedError

    def get_inflated(self, radius: float) -> Shape:
        """Return new shape expanded in all directions by radius while maintaining center"""
        raise NotImplementedError

    def get_bounding_box_area(self) -> float:
        """Return the area of the rectangle which bounds this shape"""
        raise NotImplementedError


class Circle(Shape):
    """
    Circle shape for path finding
    """
    def __init__(self, center_x: float, center_y: float, radius: float):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

    def is_vector_intersect(self, vector: Vector) -> bool:
        """Return if vector intersects the circle, tangent line should be false"""
        # TODO: This algorithm is not done. Either consider projection approach from
        #  drawings or account for the 4 cases in drawings (vert line, horizontal, pos slope, neg slope)

        # def checkCollision_linecircle(a, b, c, x, y, radius):
        # check if circle centre within vector range
        left = min(vector.start.x, vector.end.x)
        right = max(vector.start.x, vector.end.x)
        top = min(vector.start.y, vector.end.y)
        bottom = max(vector.start.y, vector.end.y)

        (right < self.center_x and self.center_y < top)
        (left > self.center_x and self.center_y > bottom)

        if True:
            # find line constants
            # ax+by+c=0
            a = vector.end.y - vector.start.y
            b = vector.start.x - vector.end.x
            c = a * vector.start.x + b * vector.start.y
            # Finding the distance of line
            # from center.
            dist = ((abs(a * self.center_x + b * self.center_y + c)) /
                    math.sqrt(a * a + b * b))

            # Checking if the distance is less
            # than, greater than or equal to radius.
            if self.radius == dist:
                return False
            elif self.radius > dist:
                return False
            else:
                return True
        else:
            return False

    def get_vertices(self, vector: Optional[Vector]) -> list[Point]:
        """Return the points where the circle intersects with the line perpendicular
        to the vector and going through the center of the circle.

        Preconditions:
            - The vector intersects the circle in 2 places
        """
        #TODO: Currently only returns 2 points, but 4 are needed to go around (reference drawings)

        # Gets the angle perpendicular to the vector's angle
        ang = math.atan2(vector.end.y - vector.start.y, vector.end.x - vector.start.x) + math.pi / 2

        # Gets the points on both sides of the perpendicular
        return [
            Point(self.center_x + self.radius * math.cos(ang),
                  self.center_y + self.radius * math.sin(ang)),
            Point(self.center_x - self.radius * math.cos(ang),
                  self.center_y - self.radius * math.sin(ang))
        ]

    def get_inflated(self, radius: float) -> Circle:
        """
        Return new circle with its radius increased by radius
        """
        return Circle(
            center_x=self.center_x,
            center_y=self.center_y,
            radius=self.radius + radius
        )

    def get_bounding_box_area(self) -> float:
        """Get bounding box area of circle"""
        return (self.radius ** 2) * 4

    def is_point_inside(self, point: Point):
        """Return if point is inside the shape. If point is on edges, does not count"""
        return dist((self.center_x, self.center_y), (point.x, point.y)) < self.radius


class Rectangle(Shape):
    """
    Rect shape for path finding
    """
    def __init__(self, left: float, top: float, width: float, height: float):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def is_vector_intersect(self, vector: Vector) -> bool:
        """Return if vector intersects rectangle, false if vector only touches edges or vertices"""
        sides = self.get_sides()
        return any(are_vectors_intersecting(side, vector) for side in sides) or self.is_vector_inside(vector)

    def get_vertices(self, vector: Optional[Vector] = None) -> list[Point]:
        """Return all 4 corners of the rectangle"""
        return [
            Point(self.left, self.top),
            Point(self.left + self.width, self.top),
            Point(self.left + self.width, self.top + self.height),
            Point(self.left, self.top + self.height)
        ]

    def get_inflated(self, radius: float):
        """
        Return new rectangle with all sides expanded in every direction by radius, preserving center
        """
        return Rectangle(
            left=self.left - radius,
            top=self.top - radius,
            width=self.width + radius * 2,
            height=self.height + radius * 2,
        )

    def get_bounding_box_area(self) -> float:
        """Do the width times the height yknow? skrrt skrrt"""
        return self.width * self.height

    def is_point_inside(self, point: Point):
        """Return if point is inside the shape. If point is on edges, does not count"""
        return self.left < point.x < self.left + self.width and \
            self.top < point.y < self.top + self.height

    def is_vector_inside(self, vector: Vector):
        """Return if start, end, or midpt of vector is inside the rectangle"""
        return self.is_point_inside(vector.start) or \
            self.is_point_inside(vector.end) or self.is_point_inside(midpoint(vector))

    def get_sides(self) -> list[Vector]:
        """Return all sides of the rectangle as vectors (start and end hold no significance for these)"""
        bot = Vector(Point(self.left, self.top + self.height),
                     Point(self.left + self.width, self.top + self.height))

        top = Vector(Point(self.left, self.top),
                     Point(self.left + self.width, self.top))

        left = Vector(Point(self.left, self.top),
                      Point(self.left, self.top + self.height))

        right = Vector(Point(self.left + self.width, self.top),
                       Point(self.left + self.width, self.top + self.height))
        return [bot, top, left, right]
