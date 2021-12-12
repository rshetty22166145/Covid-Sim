from __future__ import annotations
from geometry.geometry import *
from geometry.helpers import dist
import random


def get_paths(rects: list[Rectangle],
              vector: Vector,
              inflation_radius: float = 0.0,
              max_paths=None,
              is_random=False) -> tuple[list[Path], bool]:
    """
    Return a set of paths, each of which leads from the starting point
    of vector to its end point without intersecting any rectangles. Also return
    a boolean indicating whether the endpoint of the path is inside a rect

    Possible Optimizations/Improvements:
        - Instead of getting all the intersecting shapes each time, get the first one the comes up,
        that is, alter this in the get_intersecting_shapes func. This will sacrifice largest shape sorting
        - Check for overlapping shapes and merge them into 1 before the path finding recursion starts.
        Cache shape lists each frame with clear_cache ability in a dict for different social distancing
        values to save processing

    :param rects: Rectangle shapes of objects to avoid
    :param vector: Desired start and end points via a vector
    :param inflation_radius: Inflates all rectangles by the given value
    :param is_random: Should a random path be chosen each time (best performance)
    :param max_paths: Stop executing after this many paths have been found (better performance)
    """
    # TODO: Rectangle vector collision breaks if vector crosses diagonally through vertices!!! FiXX!!
    # TODO: Consider optimizations above

    # Inflate rectangles by person radius so person doesn't collide with shapes
    if inflation_radius != 0:
        # Do not inflate if start or endpt is in this rect
        new_rects = []
        for r in rects:
            inflated = r.get_inflated(inflation_radius)
            if inflated.is_point_inside(vector.start) or inflated.is_point_inside(vector.end):
                new_rects.append(r)
            else:
                new_rects.append(inflated)
        rects = new_rects

    was_endpt_blocked = False
    # Exclude rectangles which consume the start or endpoint.
    filtered_rects = []
    for rect in rects:
        if rect.is_point_inside(vector.end):
            was_endpt_blocked = True
        elif not rect.is_point_inside(vector.start):
            filtered_rects.append(rect)
    rects = filtered_rects

    # List of paths which to which the recursive tree will append
    paths = []

    def recursive_tree(cur_path: Path) -> None:

        # Get vectors of this path
        cur_vecs = cur_path.get_vectors()

        # Get rectangles which intersect any vector in the path
        cur_rects = [r for v in cur_vecs for r in rectangles_intersecting_vector(rects, v)]

        # If no rectangle intersects, path works and should be returned
        if len(cur_rects) == 0:
            paths.append(cur_path)

        elif max_paths is None or len(paths) < max_paths:
            largest_rect = cur_rects[0]

            # Index of point in path that is consumed by largest_shape (if any)
            point_idx = None
            # vector in path which intersects shape (if any)
            intersecting_vector = None

            # Finds if the largest shape consumes a point, and if not, checks if it intersects a vector
            # It must be one of the 2 since the shape intersects the path
            for idx in range(1, len(cur_path.points) - 1):
                if largest_rect.is_point_inside(cur_path.points[idx]):
                    point_idx = idx
                    break

            if point_idx is None:
                for vec in cur_vecs:
                    if largest_rect.is_vector_intersect(vec):
                        intersecting_vector = vec
                        break

                modified_paths = get_modified_paths_vector(largest_rect, cur_path, intersecting_vector)
                if is_random:
                    recursive_tree(random.choice(modified_paths))
                else:
                    for p in modified_paths:
                        recursive_tree(p)

    # Passes vector as an initial path
    recursive_tree(Path([vector.start, vector.end]))

    return paths, was_endpt_blocked


def get_modified_paths_vector(rect: Rectangle, path: Path, vector: Vector) -> list[Path]:
    """Return a list of new paths which modify the given path to try and avoid the given
    shape which was found intersecting the provided vector, which is part of the path"""

    # Gets shape vertices and sorts them by distance from starting pt of vector
    sorted_vertices = sorted(rect.get_vertices(), key=lambda pt: dist(tuple(vector.start), tuple(pt)))
    vec_start_path_idx = path.points.index(vector.start)
    vec_end_path_idx = path.points.index(vector.end)

    def copy_path_pts():
        return [Point(pt.x, pt.y) for pt in path.points]

    path1_points = copy_path_pts()
    path2_points = copy_path_pts()

    def case_1() -> list[Path]:
        """endpoints of vector are between edges of rect shape and are on opposite sides of rect"""
        paths = []

        for i in range(0, len(sorted_vertices) - 2):
            for j in range(2, len(sorted_vertices)):
                if sorted_vertices[j].x == sorted_vertices[i].x or sorted_vertices[j].y == \
                        sorted_vertices[i].y:

                    new_path_pts = copy_path_pts()

                    new_path_pts.insert(vec_end_path_idx, sorted_vertices[j])
                    new_path_pts.insert(vec_end_path_idx, sorted_vertices[i])

                    paths.append(Path(new_path_pts))

        return paths

    def case_2() -> list[Path]:
        """endpoints of vector are on or outside of edges of rect shape"""
        path1_points.insert(vec_end_path_idx, sorted_vertices[1])
        path2_points.insert(vec_end_path_idx, sorted_vertices[2])

        return [Path(path1_points), Path(path2_points)]

    def case_3() -> list[Path]:
        """one endpoint of vector is between edges and one is on or outside edges"""
        # Pt on vec bound box which is not bound in x or y by rect sides and not on the vector (should be 1 pt)

        outside_vert = [vert for vert in vector.get_bounding_box().get_vertices() if
                        vert != vector.start and vert != vector.end and
                        (not rect.is_point_between_edges(vert))][0]

        # Sorts shape vertices as distance from the outside vertex
        sorted_vertices_outside = sorted(rect.get_vertices(), key=lambda pt: dist(tuple(outside_vert), tuple(pt)))

        path1_points.insert(vec_end_path_idx, sorted_vertices_outside[0])

        # This should give us the 2 points for path 2
        filtered_points = [vert for vert in sorted_vertices
                           if not vector.get_bounding_box().is_point_inside_inclusive(vert)]

        path2_points.insert(vec_end_path_idx, filtered_points[1])
        path2_points.insert(vec_end_path_idx, filtered_points[0])

        return [Path(path1_points), Path(path2_points)]

    def case_4() -> list[Path]:
        """both endpoints are between edges but are on neighboring perpendicular edge sides"""

        # This should come up with the 1 other vertex which is outside of the shape but on the bound box of the vector
        outside_vert = [vert for vert in vector.get_bounding_box().get_vertices() if
                        vert != vector.start and vert != vector.end and not rect.is_point_inside(vert)][0]

        # Sorts shape vertices as distance from the outside vertex
        sorted_vertices_outside = sorted(rect.get_vertices(), key=lambda pt: dist(tuple(outside_vert), tuple(pt)))

        #
        path1_points.insert(vec_end_path_idx, sorted_vertices_outside[0])

        # Gets the sorted_vertices from starting pt which dont include [0] and [3] of sorted verts from outside vert
        filtered_verts = [vert for vert in sorted_vertices if
                          vert != sorted_vertices_outside[0] and vert != sorted_vertices_outside[3]]

        path2_points.insert(vec_end_path_idx, filtered_verts[1])
        path2_points.insert(vec_end_path_idx, sorted_vertices_outside[3])
        path2_points.insert(vec_end_path_idx, filtered_verts[0])

        return [Path(path1_points), Path(path2_points)]

    if rect.is_point_between_edges(vector.start) and rect.is_point_between_edges(vector.end):
        if (rect.is_point_between_edges(vector.start, only_vertical=True) and
            rect.is_point_between_edges(vector.end, only_vertical=True)) or \
            (rect.is_point_between_edges(vector.start, only_horizontal=True) and
             rect.is_point_between_edges(vector.end, only_horizontal=True)):
            return case_1()
        else:
            return case_4()
    elif rect.is_point_between_edges(vector.start) or rect.is_point_between_edges(vector.end):
        return case_3()
    else:
        return case_2()


def get_modified_paths_point(rect: Rectangle, path: Path, point_index: int) -> list[Path]:
    """Return a list of new paths which modify the given path to try and avoid the given
    shape which was found to be consuming the point at point_index in the path"""
    paths = []
    for pt in rect.get_vertices():
        curr_path = Path([])

        for j in range(0, len(path.points)):
            if j == point_index:
                curr_path.points.append(pt)
            else:
                curr_path.points.append(Point(path.points[j].x, path.points[j].y))
        paths.append(curr_path)
    return paths


def rectangles_intersecting_path(rects: list[Rectangle], path: Path) -> list[Rectangle]:
    """Return all shapes that intersect the given path sorted by size of rectangle bounding box
    in descending order."""
    # TODO: Make dis func yeet yeet, potential for optimization


def rectangles_intersecting_vector(rects: list[Rectangle], vector: Vector) -> list[Rectangle]:
    """Return all shapes that intersect the given vector sorted by size of rectangle bounding box
    in descending order."""
    return sorted([rect for rect in rects if rect.is_vector_intersect(vector)],
                  key=lambda r: r.get_area(), reverse=True)


def rectangles_consuming_point(rects: list[Rectangle], point: Point) -> list[Rectangle]:
    """Return all shapes that consume the point provided in descending order of bounding box size"""
    return sorted([rect for rect in rects if rect.is_point_inside(point)],
                  key=lambda r: r.get_area(), reverse=True)
