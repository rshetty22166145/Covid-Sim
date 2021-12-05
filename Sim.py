from dataclasses import dataclass
import pygame
import threading
import time


class SimManager:
    """Manages simulation progression and graphical display"""
    ZOOM_IN_VAL = 0.95
    ZOOM_OUT_VAL = 1.05

    def __init__(self):
        # Instance of city for the sim
        self.city = City(self, (500, 5))

        # All people of the city
        self.people = {Person(self, Location(None, 110, 110)) for _ in range(10)}

        # App window dimensions in pixels
        self.screen_dims = (600, 600)

        # Camera dimensions in world-terms
        self.cam = Camera([0.0, 0.0], 500, 1)

        # App window and running flag
        self.screen = pygame.display.set_mode(self.screen_dims, pygame.DOUBLEBUF)
        self.running = True

        # Computational thread
        self.sim_thread = threading.Thread(target=self.run_sim)

    def start(self):
        """Start sim, run graphical interface for the simulation"""
        #self.sim_thread.start()

        while self.running:
            # Clear screen
            self.screen.fill((0, 0, 0))

            # Event handler
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False

                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self.scroll_manager(e)

            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.cam.topleft[0] += 5.0
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                self.cam.topleft[0] -= 5.0
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                self.cam.topleft[1] += 5.0
            if pygame.key.get_pressed()[pygame.K_UP]:
                self.cam.topleft[1] -= 5.0

            self.render()

            # Display update
            pygame.display.update()

    def scroll_manager(self, mouse_event):
        e = mouse_event

        # Gets mouse position relative to screen
        mp_old = pygame.mouse.get_pos()
        # Stores former camera width
        old_cam_width = self.cam.width

        # Zooms out using the center of the screen as pivot
        if e.button == pygame.BUTTON_WHEELDOWN:
            # Applies zoom by scaling camera size
            self.cam.width *= self.ZOOM_OUT_VAL

            # Calculates cam width diff and shifts cam by half of that
            # This causes the cam to zoom out using the center of the screen
            self.cam.topleft[0] += (old_cam_width - self.cam.width) / 2
            self.cam.topleft[1] += ((old_cam_width * self.cam.height_frac) - (
                        self.cam.width * self.cam.height_frac)) / 2

        # Zooms in using the mouse position as pivot
        elif e.button == pygame.BUTTON_WHEELUP:
            # Applies zoom by scaling camera size
            self.cam.width *= self.ZOOM_IN_VAL

            # Scales the mouse position based on zoom
            # (even though mouse didnt actually change pos relative to window)
            mp_new = mp_old[0] * self.ZOOM_IN_VAL, mp_old[1] * self.ZOOM_IN_VAL

            # Gets the difference between mouse positions and scales the values
            # to be relative to world dimensions
            diff = ((mp_old[0] - mp_new[0]) * (self.cam.width / self.screen_dims[0]),
                    (mp_old[1] - mp_new[1]) * ((self.cam.width * self.cam.height_frac) / self.screen_dims[1]))

            # Shifts camera (which uses world dimensions) by the diff to zoom towards mouse
            self.cam.topleft[0] += diff[0]
            self.cam.topleft[1] += diff[1]

    def render(self):
        """
        Renders simulation frame using camera object and world data from sim
        """
        cam_rect = pygame.Rect(self.cam.topleft, (self.cam.width, self.cam.width * self.cam.height_frac))
        ratio = self.screen_dims[0] / cam_rect.width

        for b in self.city.buildings:
            if cam_rect.colliderect(b.rect):
                scaled_b_topleft = (b.rect.topleft[0] * ratio,
                                    b.rect.topleft[1] * ratio)
                scaled_cam_topleft = (cam_rect.topleft[0] * ratio,
                                      cam_rect.topleft[1] * ratio)
                relative_b_topleft = (scaled_b_topleft[0] - scaled_cam_topleft[0],
                                      scaled_b_topleft[1] - scaled_cam_topleft[1])

                blit_rect = pygame.Rect(relative_b_topleft, (b.rect.width * ratio, b.rect.height * ratio))

                pygame.draw.rect(self.screen, (0, 200, 150), blit_rect)

    def run_sim(self):
        """Execute simulation """
        count = 0
        while self.running:
            print(str(count := count + 1) + "...")


class City:
    def __init__(self, sim, grid_dims):
        # Parent sim manager object
        self.sim = sim

        self.grid = grid_dims
        self.road_width = 40
        self.plot_dims = (100, 100)

        self.buildings = {Building(self,
                                   (x * (self.plot_dims[0] + self.road_width) + 10,
                                    y * (self.plot_dims[1] + self.road_width) + 10),
                                   (90, 90)) for x in range(self.grid[0]) for y in range(self.grid[1])}


class Building:
    def __init__(self, sim, topleft, wh: tuple[int, int]):
        # Parent sim manager object
        self.sim = sim

        # World-scale Rect info
        self.rect = pygame.Rect(topleft, wh)


@dataclass
class Location:
    """
    World-scale location for Person objects
    """
    building: Building  # None if outside
    x: float  # Relative to building topleft if inside building
    y: float  # Relative to building topleft if inside building


class Person:
    def __init__(self, sim, location: Location):
        # Parent sim manager object
        self.sim = sim

        # location descriptor class, not to be directly modified
        self.location = location

        # TODO: Assert that person's initial location is valid (inside building if inside, not inside building if out)


@dataclass
class Camera:
    topleft: list  # World-scale position of camera's topleft
    width: int  # World-scale width of camera (changed with zoom)
    height_frac: float  # value to multiply width by to get height
