import pygame
from component_properties import Property, NumericProperty
from typing import Union, Optional


class Component:
    """
    Defines the parent class of all GUI components
    """
    def __init__(self, **kwargs: Property):
        self.parent: Optional[Component] = None

        # Property list, initially defaults.
        self.properties = {"height": NumericProperty(0.0, component=self),
                           "width": NumericProperty(0.0, component=self),
                           "top": NumericProperty(0.0, component=self),
                           "left": NumericProperty(0.0, component=self)}
        # Adds any specified props and overrides defaults
        self.add_properties(**kwargs)

        # Creates component surface
        self.__surface = self.generate_surface()

        # Whether to disable user interaction with this component
        self.__disable_interaction = False

    def generate_surface(self):
        """Return a new surface for this component based on its properties"""
        return pygame.Surface((self.properties["width"].get_value(),
                               self.properties["height"].get_value()),
                              flags=pygame.SRCALPHA, depth=32).convert_alpha()

    def get_genuine_pos(self) -> tuple[float, float]:
        """
        Return the top,left position of this component relative to the topmost parent
        instead of the immediate one.
        Topmost parent is always the window
        """
        x = self.properties["left"].get_value()
        y = self.properties["top"].get_value()
        c = self.parent
        while c is not None:
            x += c.properties["left"].get_value()
            y += c.properties["top"].get_value()
            c = c.parent
        return x, y

    def add_properties(self, **kwargs: Property):
        """
        Add specified kwargs to property dict
        """
        for prop_name in kwargs:
            # Add Property and ensure that special props are of the correct type
            if prop_name in ("height", "width", "top", "left"):
                assert isinstance(kwargs[prop_name], NumericProperty)
            self.properties[prop_name] = kwargs[prop_name]
            # Finalize property
            self.properties[prop_name].finalize(self)

    def handle_component(self, events):
        """Handles own events and renders self"""
        self.handle_events(events)
        self.render_component()

    def handle_events(self, events):
        """
        React to pygame events. This method is not abstract and does
        not have to be implemented for non-interactable components
        """
        pass

    def render_component(self):
        """
        If the component needs rendering instructions for each frame,
        put them here. Blit directly onto self.__surface
        """
        raise NotImplementedError

    def get_surface(self):
        return self.__surface

    def disable_interaction(self):
        self.__disable_interaction = True

    def enable_interaction(self):
        self.__disable_interaction = False


class Container(Component):
    """
    A component which can have children
    """
    def __init__(self, **kwargs: Property):
        Component.__init__(self, **kwargs)

        self.__children = set()

    def add_child(self, child) -> None:
        """Set child's parent to self and add child to children"""
        child.parent = self
        self.__children.add(child)

    def handle_component(self, events):
        """Renders component as well as its children, and also calls event handlers"""
        self.handle_events(events)
        self.render_component()

        for child in self.__children:
            # Handles component for each child
            child.handle_component(events)

            # Draws child surface relative to container surface
            self.__surface.blit(child.get_surface(), (child.properties["left"].get_value(),
                                                      child.properties["top"].get_value()))

    def render_component(self):
        raise NotImplementedError


class WindowComponent(Container):
    """
    Stores the main pygame window
    """
    def __init__(self, window: pygame.Surface, width: int, height: int, background_color=(0, 0, 0)):
        # Window is a container with no parents
        Container.__init__(self,
                           width=NumericProperty(width),
                           height=NumericProperty(height),
                           background_color=Property(background_color))

        # Surface set to app display window
        self.__surface = window

    def render_component(self):
        # Clears surface with a fill
        self.__surface.fill(self.properties["background_color"].get_value())
