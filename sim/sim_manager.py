from enum import IntEnum
from sim.sim_components import *


# Keeps track of graphics data
class GraphicsData:

    class Types(IntEnum):
        STATIC = 0
        DYNAMIC = 1
        BOTH = 2
    """
    Attributes:
        - buildings: List of building locations (id, top, left, width, height)
        - people: List of people info (id, is_infected, x, y) potentially more later
        - objects: List of interactables, (id, top, left, width, height)
    """
    def __init__(self):
        self.buildings: list[tuple[int, int, int, int, int]] = []
        self.people: list[tuple[int, bool, int, int]] = []
        self.objects: list[tuple[int, int, int, int, int]] = []
    
    def get_dynamic_sendable_info(self):
        return {"type": GraphicsData.Types.DYNAMIC.value,
                "people": self.people}

    def get_static_sendable_info(self):
        return {"type": GraphicsData.Types.STATIC.value,
                "buildings": self.buildings,
                "objects": self.objects}

    def get_all_sendable_info(self):
        return {"type": GraphicsData.Types.BOTH.value,
                "buildings": self.buildings,
                "objects": self.objects,
                "people": self.people}


class SimManager:
    def __init__(self):
        self.__graphics_data = GraphicsData()

        # DEBUG: Creates arbitrary building, object, and people graphical data
        self.__graphics_data.buildings = [tuple(i for _ in range(5)) for i in range(10)]
        self.__graphics_data.objects = [tuple(i for _ in range(5)) for i in range(20, 30)]
        self.__graphics_data.people = [tuple(i for _ in range(5)) for i in range(40, 50)]

        #
        self.city = City()

    def progress_simulation(self, time_delta_ms: int) -> dict:
        """
        Progress the simulation world by the provided time_delta_ms in simulation
        world time measurement

        Preconditions:
            - time_delta_ms > 0
        """
        return self.__graphics_data.get_dynamic_sendable_info()

    def get_static_graphics_data(self) -> dict:
        """
        Return info on static simulation objects such as buildings and interactables
        """
        return self.__graphics_data.get_static_sendable_info()
