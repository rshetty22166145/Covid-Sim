"""Synchronous App

Module Description
==================
This module implements an App class which engages with the simulation synchronously when
called by the launcher.

Copyright and Usage Information
===============================

This file pertains to the CovSim simulation software. The code inside
this file may be viewed by CSC faculty at University of Toronto. Otherwise,
this code is only to be used by running the program. Distributing or
using this code in any other way is prohibited.

This file is Copyright (c) 2021 Aleksey Panas, Rohit Shetty.
"""
from dataclasses import dataclass
from sim.sim_manager import SimManager, SimParams
from geometry.geometry import *
import logging
import pygame
import colorsys
pygame.init()


@dataclass
class Camera:
    """
    Used for 2D renderers to keep track of the camera's view into the simulation world
    for rendering purposes

    Instance Attributes:
        - topleft: World-scale position of camera's topleft
        - width: World-scale width of camera (changed with zoom)
        - height_frac: value to multiply width by to get height
    """
    topleft: list
    width: int
    height_frac: float


class SyncApp:
    """
    Runs simulation graphics and the simulation itself on the same process. This
    class will later be deleted and the App class will be used in place of it,
    when everything is complete

    Instance Attributes:
        - SCREEN_DIMS: user screen dimensions constant
        - WINDOW_DIMS: window dimensions constant
        - _clock: pygame ticker clock
        - _window: app window
        - _is_running: main loop flag
        - _events: pygame event list
        - _sim: the sim object
        - _sim_speed_s: By how many seconds the sim should be progressed each frame
        - _camera: Eyes to see the world
    """
    SCREEN_SIZE_CONSTANT = 0.7
    ZOOM_IN_VAL = 0.95
    ZOOM_OUT_VAL = 1.05

    def __init__(self, param_dict: dict):
        # User screen dimensions, and app window dimensions
        self.SCREEN_DIMS = (pygame.display.Info().current_w,
                            pygame.display.Info().current_h)
        self.WINDOW_DIMS = (int(min(self.SCREEN_DIMS) * SyncApp.SCREEN_SIZE_CONSTANT),) * 2
        logging.info("Window dims are " + str(self.WINDOW_DIMS))

        # Pygame tick clock
        self._clock = pygame.time.Clock()

        # Window object
        self._window = pygame.display.set_mode(self.WINDOW_DIMS)

        self._is_running = True
        # Event queue gotten from pygame each frame
        self._events = []

        # Sim manager object
        self._sim = SimManager(self.parse_params(param_dict))

        # Seconds to progress the sim by each frame
        self._sim_speed_s = 5

        self._camera = Camera(topleft=[-20, -20], width=self._sim.city.get_bounding_box().width+40,
                              height_frac=self.WINDOW_DIMS[1] / self.WINDOW_DIMS[0])

        # Log the people
        for p in self._sim.city.people:
            logging.info(str(p))

    def parse_params(self, param_dict: dict) -> SimParams:
        """Takes the parameter dict passed in from the GUI and converts
        it to a SimParams object directly passable into the SimManager initializer"""
        return SimParams(**param_dict)

    def start(self):
        """Start main app loop"""
        self.run_sim()

    def stop(self):
        """Stop main app loop"""
        self._is_running = False

    def run_sim(self):
        """Runs main app loop"""
        while self._is_running:
            self._window.fill((70, 70, 70))

            # Progresses simulation
            self._sim.progress_simulation(self._sim_speed_s)

            # Stores events, captures quit event
            self._events = pygame.event.get()
            for event in self._events:
                if event.type == pygame.QUIT:
                    self.stop()
                # Camera zoom feature
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.scroll_manager(event)

            # camera movement
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self._camera.topleft[0] += 5.0
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                self._camera.topleft[0] -= 5.0
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                self._camera.topleft[1] += 5.0
            if pygame.key.get_pressed()[pygame.K_UP]:
                self._camera.topleft[1] -= 5.0

            # Render sim objects
            self.render()

            for b in self._sim.city.buildings:
                draw_rect(b.rect, self._window, (255, 255, 255))
                draw_circle(Circle(b.entrance_point.x, b.entrance_point.y, 7), self._window, (255, 255, 255))

            for p in self._sim.city.people:
                if p.location.point is not None:
                    pt = p.location.point
                    draw_circle(Circle(pt.x, pt.y, 4), self._window,
                                (255, 0, 0) if p.is_infected else (0, 255, 0), width=0)
            draw_paths([p.current_path for p in self._sim.city.people], self._window, start_circle=False)

            pygame.display.update()
            self._clock.tick(100)
            pygame.display.set_caption("CovSim    FPS: " + str(self._clock.get_fps()))

    def render(self):
        """Renders simulation frame using camera object and world data from sim"""
        cam_rect = pygame.Rect(self._camera.topleft, (self._camera.width,
                                                      self._camera.width * self._camera.height_frac))
        ratio = self.WINDOW_DIMS[0] / cam_rect.width

        self.render_buildings(ratio, cam_rect)

    def render_buildings(self, ratio: float, cam_rect: pygame.Rect):
        """Renders buildings using camera"""
        for b in self._sim.city.buildings:
            # Building pygame rectangle
            b_pyrect = b.rect.get_pygame_rectangle()

            if cam_rect.colliderect(b_pyrect):
                blit_rect = pygame.Rect(SyncApp.get_relative_pos(b_pyrect.topleft, ratio, cam_rect),
                                        (b_pyrect.width * ratio,
                                         b_pyrect.height * ratio))

                pygame.draw.rect(self._window, (0, 200, 150), blit_rect)

    @staticmethod
    def get_relative_pos(
            world_pos: Union[tuple[float, float], list, Point],
            ratio: float, cam_rect: pygame.Rect
    ) -> tuple[int, int]:
        """Given a sim world position, find the position in pixels relative to the topleft
        of the window"""
        scaled_pos = (world_pos[0] * ratio,
                      world_pos[1] * ratio)
        scaled_cam_topleft = (cam_rect.topleft[0] * ratio,
                              cam_rect.topleft[1] * ratio)
        relative_pos = (int(scaled_pos[0] - scaled_cam_topleft[0]),
                        int(scaled_pos[1] - scaled_cam_topleft[1]))
        return relative_pos

    def scroll_manager(self, mouse_event):
        e = mouse_event

        # Gets mouse position relative to screen
        mp_old = pygame.mouse.get_pos()
        # Stores former camera width
        old_cam_width = self._camera.width

        # Zooms out using the center of the screen as pivot
        if e.button == pygame.BUTTON_WHEELDOWN:
            # Applies zoom by scaling camera size
            self._camera.width *= self.ZOOM_OUT_VAL

            # Calculates cam width diff and shifts cam by half of that
            # This causes the cam to zoom out using the center of the screen
            self._camera.topleft[0] += (old_cam_width - self._camera.width) / 2
            self._camera.topleft[1] += ((old_cam_width * self._camera.height_frac) - (
                        self._camera.width * self._camera.height_frac)) / 2

        # Zooms in using the mouse position as pivot
        elif e.button == pygame.BUTTON_WHEELUP:
            # Applies zoom by scaling camera size
            self._camera.width *= self.ZOOM_IN_VAL

            # Scales the mouse position based on zoom
            # (even though mouse didnt actually change pos relative to window)
            mp_new = mp_old[0] * self.ZOOM_IN_VAL, mp_old[1] * self.ZOOM_IN_VAL

            # Gets the difference between mouse positions and scales the values
            # to be relative to world dimensions
            diff = ((mp_old[0] - mp_new[0]) * (self._camera.width / self.screen_dims[0]),
                    (mp_old[1] - mp_new[1]) * ((self._camera.width * self._camera.height_frac) / self.screen_dims[1]))

            # Shifts camera (which uses world dimensions) by the diff to zoom towards mouse
            self._camera.topleft[0] += diff[0]
            self._camera.topleft[1] += diff[1]


def draw_paths(paths: list[Path], screen: pygame.Surface, start_circle=True, circles=False):
    """Draws a list of paths"""
    cols = color_brewer(len(paths))
    for i in range(len(paths)):
        draw_path(paths[i], screen, cols[i], start_circle=start_circle, circles=circles)


def draw_rect(rectangle: Rectangle, screen: pygame.Surface, color: tuple[int, int, int], width=1):
    """Draws a rectangle"""
    pygame.draw.rect(screen, color,
                     pygame.Rect((int(rectangle.left), int(rectangle.top)),
                                 (int(rectangle.width), int(rectangle.height))), width=width)


def draw_circle(circle: Circle, screen: pygame.Surface, color: tuple[int, int, int], width=1):
    """Draws a circle"""
    pygame.draw.circle(screen, color, (circle.center_x, circle.center_y), circle.radius, width=width)


def draw_path(path: Path, screen: pygame.Surface, color: tuple[int, int, int],
              start_circle=True, circles=False):
    """Draws a single path"""
    vecs = path.get_vectors()

    for vec in vecs:
        draw_vector(vec, screen, color, start_circle=(3 if circles else 0))

    # Draws circle at start of path
    if start_circle:
        draw_circle(Circle(center_x=vecs[0].start.x, center_y=vecs[0].start.y, radius=3), screen, color, width=0)


def draw_vector(vector: Vector, screen: pygame.Surface, color: tuple[int, int, int],
                start_circle=0, end_circle=0):
    """Draws a single vector with optional endpoint circles"""
    pygame.draw.line(screen, color, (vector.start.x, vector.start.y), (vector.end.x, vector.end.y))
    if start_circle > 0:
        draw_circle(Circle(center_x=vector.start.x, center_y=vector.start.y, radius=start_circle), screen, color,
                    width=1)
    if end_circle > 0:
        draw_circle(Circle(center_x=vector.end.x, center_y=vector.end.y, radius=end_circle), screen, color, width=1)


def color_brewer(num: int) -> list[tuple[int, ...]]:
    """Returns an equally spaced list of colors with length of num"""
    if num == 0:
        return []
    val = 0.7 / num
    return [tuple(int(c * 255) for c in colorsys.hsv_to_rgb(i * val, 0.8, 0.8)) for i in range(num)]
