from my_path_finding.geometry import *
from my_path_finding.helpers import dist


def get_paths(shapes: list[Shape],
              vector: Vector,
              person_radius: float = 0.0) -> list[Path]:
    """
    Return a set of paths, each of which leads from the starting point
    of vector to its end point without intersecting any shapes

    Possible Optimizations:
        - Instead of getting all the intersecting shapes each time, get the first one the comes up,
        that is, alter this in the get_intersecting_shapes func. This will sacrifice largest shape sorting
        - Instead of finding all paths choose random path
    """
    # Inflates shapes by person radius so person doesnt collide with shapes
    if person_radius != 0:
        shapes = [s.get_inflated(person_radius) for s in shapes]

    # List of paths which to which the recursive tree will append
    paths = []

    def recursive_tree(cur_path: Path) -> None:

        # Gets vectors of this path
        cur_vecs = cur_path.get_vectors()

        # Get shapes which intersect any vector in the path
        cur_shapes = [shape for v in cur_vecs for shape in shapes_intersecting_vector(shapes, v)]

        # If no shape intersects, path works and should be returned
        if len(cur_shapes) == 0:
            paths.append(cur_path)

        else:
            largest_shape = cur_shapes[0]

            # Index of point in path that is consumed by largest_shape (if any)
            point_idx = None
            # vector in path which intersects shape (if any)
            intersecting_vector = None

            # Finds if the largest shape consumes a point, and if not, checks if it intersects a vector
            # It must be one of the 2 since the shape intersects the path
            for idx in range(1, len(cur_path.points) - 1):
                if largest_shape.is_point_inside(cur_path.points[idx]):
                    point_idx = idx
                    break

            if point_idx is None:
                for vec in cur_vecs:
                    if largest_shape.is_vector_intersect(vec):
                        intersecting_vector = vec
                        break



    # Passes vector as an initial path
    recursive_tree(Path([vector.start, vector.end]))

    new_paths = [Path([vec.start for vec in path]) for path in paths]
    for i in range(len(new_paths)):
        new_paths[i].points.append(paths[i][-1].end)
    return new_paths


def get_modified_paths_vector(shape: Shape, path: Path, vector: Vector) -> list[Path]:
    """Return a list of new paths which modify the given path to try and avoid the given
    shape which was found intersecting the provided vector, which is part of the path"""
    sorted_vertices = sorted(shape.get_vertices(), key=lambda pt: dist(tuple(vector.start), tuple(pt)))
    vec_start_path_idx = path.points.index(vector.start)
    vec_end_path_idx = path.points.index(vector.end)

    def copy_path_pts():
        return [Point(pt.x, pt.y) for pt in path.points]

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
        path1_points = copy_path_pts()
        path2_points = copy_path_pts()

        path1_points.insert(vec_end_path_idx, sorted_vertices[1])
        path2_points.insert(vec_end_path_idx, sorted_vertices[2])

        return [Path(path1_points), Path(path2_points)]

    def case_3() -> list[Path]:
        """one endpoint of vector is between edges and one is on or outside edges"""
        pass

    def case_4() -> list[Path]:
        """both endpoints are between edges but are on neighboring perpendicular edge sides"""
        pass

    return case_1()


def get_modified_paths_point(shape: Shape, path: Path, point_index: int) -> list[Path]:
    """Return a list of new paths which modify the given path to try and avoid the given
    shape which was found to be consuming the point at point_index in the path"""
    paths = []
    for pt in shape.get_vertices():
        curr_path = Path([])

        for j in range(0, len(path.points)):
            if j == point_index:
                curr_path.points.append(pt)
            else:
                curr_path.points.append(Point(path.points[j].x, path.points[j].y))
        paths.append(curr_path)
    return paths


def shapes_intersecting_vector(shapes: list[Shape], vector: Vector) -> list[Shape]:
    """Return all shapes that intersect the given vector sorted by size of rectangle bounding box
    in descending order."""
    return sorted([shape for shape in shapes if shape.is_vector_intersect(vector)],
                  key=lambda shape: shape.get_bounding_box_area(), reverse=True)


def shapes_consuming_point(shapes: list[Shape], point: Point) -> list[Shape]:
    """Return all shapes that consume the point provided in descending order of bounding box size"""
    return sorted([shape for shape in shapes if shape.is_point_inside(point)],
                  key=lambda shape: shape.get_bounding_box_area(), reverse=True)
