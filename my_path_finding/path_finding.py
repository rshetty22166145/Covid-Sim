from my_path_finding.geometry import *


def get_paths(shapes: list[Shape],
              vector: Vector,
              person_radius: float = 0.0) -> list[Path]:
    """
    Return a set of paths, each of which leads from the starting point
    of vector to its end point without intersecting any shapes

    Possible Optimizations:
        - Circle vertices don't need to be checked for intersection, both circle vertices will always be valid
        - Instead of finding all paths (for loop in recursion), choose random path
    """
    # Inflates shapes by person radius so person doesnt collide with shapes
    if person_radius != 0:
        shapes = [s.get_inflated(person_radius) for s in shapes]

    # Set of paths which will be modified by the recursive tree
    paths = []

    def recursive_tree(cur_vec: Vector,
                       path_history=()) -> None:

        # List of shapes intersecting with vector ordered by distance from starting pt (ascending)
        cur_shapes = get_intersecting_shapes(shapes, cur_vec)

        # If all shapes have been successfully bypassed, then a path was formed
        if len(cur_shapes) == 0:
            paths.append(path_history + (cur_vec,))
        else:
            shape = cur_shapes[0]
            vertices = shape.get_vertices(cur_vec)

            # Vectors going from the start of cur_vec to each vertex
            start_to_vertex_vectors = [Vector(start=cur_vec.start, end=v) for v in vertices]
            # Vectors going from each vertex to the enc of cur_vec
            vertex_to_end_vectors = [Vector(start=v, end=cur_vec.end) for v in vertices]

            # A vertex is only accepted if its corresponding vectors in the above 2 vector
            # lists don't intersect the shape
            vertices = [
                vertices[i] for i in range(len(vertices))
                if not(
                    shape.is_vector_intersect(start_to_vertex_vectors[i]) or
                    shape.is_vector_intersect(vertex_to_end_vectors[i])
                )]
            # Initiates recursion for each valid vertex
            for vertex in vertices:
                # passes all but first shape, passes new vector from the vertex to the end of the current one
                # Adds segment from start to vertex to the path history
                recursive_tree(Vector(start=vertex, end=cur_vec.end),
                               path_history=path_history + (Vector(start=cur_vec.start, end=vertex),))

    recursive_tree(vector)

    new_paths = [Path([vec.start for vec in path]) for path in paths]
    for i in range(len(new_paths)):
        new_paths[i].points.append(paths[i][-1].end)
    return new_paths


def get_shortest_path(paths: set[list[Vector]]) -> list[Vector]:
    """Return the shortest path from the paths provided"""


def get_intersecting_shapes(shapes: list[Shape],
                            vector: Vector
                            ) -> list[Shape]:
    """
    Return all shapes that intersect the given vector
    """
    return [shape for shape in shapes if shape.is_vector_intersect(vector)]
