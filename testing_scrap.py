import pygame
from contextlib import contextmanager
from geometry.path_finding import get_paths, get_modified_paths_point, get_modified_paths_vector
from geometry.geometry import *
import colorsys
import random
from sim.city_generator import get_city_rectangle_layout
pygame.init()

SCREEN_SIZE = (720, 720)


@contextmanager
def draw_stuff(w=SCREEN_SIZE[0], h=SCREEN_SIZE[1]):
    screen = pygame.display.set_mode((w, h))
    screen.fill((70, 70, 70))

    yield screen

    pygame.event.clear()
    pygame.display.update()
    pygame.event.set_blocked(None)
    pygame.event.set_allowed(pygame.QUIT)
    pygame.event.wait()


def draw_paths(paths: list[Path], screen: pygame.Surface):
    cols = color_brewer(len(paths))
    for i in range(len(paths)):
        draw_path(paths[i], screen, cols[i])


def draw_rect(rectangle: Rectangle, screen: pygame.Surface, color: tuple[int, int, int], width=1):
    pygame.draw.rect(screen, color,
                     pygame.Rect((int(rectangle.left), int(rectangle.top)),
                                 (int(rectangle.width), int(rectangle.height))), width=width)


def draw_circle(circle: Circle, screen: pygame.Surface, color: tuple[int, int, int], width=1):
    pygame.draw.circle(screen, color, (circle.center_x, circle.center_y), circle.radius, width=width)


def draw_path(path: Path, screen: pygame.Surface, color: tuple[int, int, int]):
    vecs = path.get_vectors()

    for vec in vecs:
        draw_vector(vec, screen, color)

    # Draws circle at start of path
    draw_circle(Circle(center_x=vecs[0].start.x, center_y=vecs[0].start.y, radius=3), screen, color, width=0)


def draw_vector(vector: Vector, screen: pygame.Surface, color: tuple[int, int, int],
                start_circle=0, end_circle=0):
    pygame.draw.line(screen, color, (vector.start.x, vector.start.y), (vector.end.x, vector.end.y))
    if start_circle > 0:
        draw_circle(Circle(center_x=vector.start.x, center_y=vector.start.y, radius=start_circle), screen, color, width=1)
    if end_circle > 0:
        draw_circle(Circle(center_x=vector.end.x, center_y=vector.end.y, radius=end_circle), screen, color, width=1)


def color_brewer(num: int) -> list[tuple[int, ...]]:
    if num == 0:
        return []
    val = 0.7 / num
    return [tuple(int(c * 255) for c in colorsys.hsv_to_rgb(i * val, 0.8, 0.8)) for i in range(num)]


def random_shape_path_test():
    rects = []

    # for _ in range(25):
    #     left = random.randint(20, SCREEN_SIZE[0] - 20)
    #     top = random.randint(20, SCREEN_SIZE[1] - 20)
    #     width = random.randint(0, SCREEN_SIZE[0] - left)
    #     height = random.randint(0, SCREEN_SIZE[1] - top)
    #     width = 20
    #     height = 20
    #     rects.append(Rectangle(left=left, top=top, width=width, height=height))

    for x in range(10):
        for y in range(10):
            width = 20
            height = 20
            gap = 20

            left = width + (width + gap) * x
            top = height + (height + gap) * y

            rects.append(Rectangle(left=left, top=top, width=width, height=height))

    rects = get_city_rectangle_layout(4, 4, 100, 40, 100)

    shapes = rects

    surf = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    path_vector = Vector(Point(x=SCREEN_SIZE[0] - 20, y=SCREEN_SIZE[1] - 20), Point(x=20, y=20))

    index = 0

    running = True
    while running:
        surf.fill((70, 70, 70))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                [path_vector.start, path_vector.end][index].x = pygame.mouse.get_pos()[0]
                [path_vector.start, path_vector.end][index].y = pygame.mouse.get_pos()[1]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    index = 0
                elif event.key == pygame.K_2:
                    index = 1

        paths, is_endpt_blocked = get_paths(shapes, path_vector, person_radius=0, max_paths=10)

        for rect in rects:
            draw_rect(rect, surf, (255, 255, 255))
        draw_paths(paths, surf)

        pygame.display.update()
        clock.tick(200)
        pygame.display.set_caption("CovSim    FPS: " + str(clock.get_fps()))


def rect_collision_test():
    rect = Rectangle(100, 100, 100, 100)
    vecs = [
        # point on edge
        Vector(Point(150, 50), Point(150, 100)),
        Vector(Point(200, 150), Point(250, 150)),
        # point on vertex

        # equal to edge
        Vector(Point(90, 100), Point(210, 100)),
        Vector(Point(100, 100), Point(100, 200)),
        Vector(Point(110, 200), Point(190, 200)),
        Vector(Point(200, 100), Point(200, 200)),

        # contains edge

        # contained by edge

        # crosses vertex
        Vector(Point(150, 50), Point(250, 150)),
        Vector(Point(150, 250), Point(250, 150)),
        Vector(Point(200, 100), Point(10, 10))
    ]

    with draw_stuff(500, 500) as surf:
        draw_rect(rect, surf, (255, 255, 255))

        for vec in vecs:
            col = (255, 0, 0) if rect.is_vector_intersect(vec) else (0, 255, 0)
            draw_vector(vec, surf, col, start_circle=5, end_circle=5)


def test_modified_path_points():
    rect = Rectangle(100, 100, 100, 100)
    path = Path([Point(10, 150), Point(150, 170), Point(300, 50)])

    new_paths = get_modified_paths_point(rect, path, 1)

    with draw_stuff(500, 500) as surf:
        draw_rect(rect, surf, (255, 255, 255))
        draw_path(path, surf, (0, 0, 0))

        draw_paths(new_paths, surf)


def test_city_layout():
    buildings = SimManager.generate_city(4, 4, 100, 70, 100)

    with draw_stuff() as surf:
        for rect in buildings:
            draw_rect(rect, surf, (255, 255, 255), width=0)


def test_modified_path_vectors():
    rect = Rectangle(100, 100, 100, 100)
    path = Path([Point(150, 90), Point(80, 300)])

    index = 0

    surf = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    running = True
    while running:
        surf.fill((70, 70, 70))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                path.points[index] = Point(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    index = 0
                elif event.key == pygame.K_2:
                    index = 1

        new_paths = get_modified_paths_vector(rect, path, Vector(path.points[0], path.points[1]))
        draw_rect(rect, surf, (255, 255, 255))
        draw_path(path, surf, (0, 0, 0))
        draw_paths(new_paths, surf)

        pygame.display.update()
        clock.tick(200)
        pygame.display.set_caption("CovSim    FPS: " + str(clock.get_fps()))


random_shape_path_test()
