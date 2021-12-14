"""Pygame GUI Package: Rectangle

Module Description
==================
This module contains the rectangle component, which creates a
sample rectangle which can be hovered over to change color. This
component was used to test the GUI.

Copyright and Usage Information
===============================

This file pertains to the CovSim simulation software. The code inside
this file may be viewed by CSC faculty at University of Toronto. Otherwise,
this code is only to be used by running the program. Distributing or
using this code in any other way is prohibited.

This file is Copyright (c) 2021 Aleksey Panas, Rohit Shetty.
"""
from my_pygame_gui.component import Component
from my_pygame_gui.component_properties import Property, NumericProperty
from typing import Any
import pygame


class RectangleComponent(Component):
    """
    Rectangle component which displays a filled rectangle of a certain
    color and has potential to change color when hovered over

    Acceptable Properties:
        - width, height, top, left: mandatory for all components
        - color: 3-int tuple for rgb color
        - hover_color: 3-int tuple for rgb color on mouse hover
    """
    DEFAULT_COLOR = (0, 0, 0)

    def __init__(self, **kwargs: Property):
        # Adds default property values to kwargs
        kwargs["color"] = Property(RectangleComponent.DEFAULT_COLOR) if \
            "color" not in kwargs else kwargs["color"]

        kwargs["hover_color"] = Property(kwargs["color"].get_pure_value()) \
            if "hover_color" not in kwargs else kwargs["hover_color"]

        # Sends in default properties along with specified ones
        Component.__init__(self, **kwargs)

        self.is_hover = False
        self.is_dirty = True

    def generate_surface(self):
        """Creates non-transparent rectangular surface"""
        return pygame.Surface((self.properties["width"].get_value(),
                               self.properties["height"].get_value())
                              ).convert_alpha()

    def handle_events(self, events):
        old_hover = self.is_hover
        if pygame.Rect(
                self.get_genuine_pos(),
                (self.properties["width"].get_value(),
                 self.properties["height"].get_value())
        ).collidepoint(pygame.mouse.get_pos()):
            self.is_hover = True
        elif self.is_hover:
            self.is_hover = False

        if not self.is_hover == old_hover:
            self.is_dirty = True

    def on_update_property(self, name: str, old_value: Any):
        self.is_dirty = True

    def render_component(self):
        if self.is_dirty:
            print((self.properties["width"].get_value(),
                   self.properties["height"].get_value()))
            col = self.properties["color"].get_value() if not \
                self.is_hover else self.properties["hover_color"].get_value()

            self._surface = self.generate_surface()
            self._surface.fill(col)
            self.is_dirty = False
