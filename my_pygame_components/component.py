import pygame
from my_pygame_components.component_properties import Property, NumericProperty
from typing import Union, Optional, Any
import logging


class Component:
    """
    Defines the parent class of all GUI components
    """
    def __init__(self, **kwargs: Property):
        self.parent: Optional[Component] = None

        # Whether to disable user interaction with this component
        self._disable_interaction = False
        # Disables interaction and hides component. Applies to container children
        self._disable_component = False

        # Property list, initially defaults.
        self.properties = {"height": NumericProperty(0.0, component=self),
                           "width": NumericProperty(0.0, component=self),
                           "top": NumericProperty(0.0, component=self),
                           "left": NumericProperty(0.0, component=self)}

        # Initially component is un-finalized with props not yet added
        # add_child calls finalize after parent is set
        self._is_finalized = False
        self._surface = None
        self._kwargs = kwargs

    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return type(self).__name__

    def update_property(self, name: str, new_value: Any) -> bool:
        """Update specified property's value and calls a reaction method.
        Return success"""
        old_value = self.properties[name].get_value()
        # Updates value, if successful, call reaction
        if self.properties[name].update_value(new_value):
            self.on_update_property(name, old_value)
            return True
        return False

    def on_update_property(self, name: str, old_value: Any):
        pass

    def finalize(self):
        # Adds any specified props and overrides defaults
        self.add_properties(**self._kwargs)
        self._kwargs = {}

        # Creates component surface
        self._surface = self.generate_surface()

        self._is_finalized = True

        logging.info(str(self) + " has finalized, with properties: " + str(self.properties))

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
            self.add_property(prop_name, kwargs[prop_name], allow_override=True)

    def add_property(self, name: str, prop: Property, allow_override=False) -> bool:
        """Adds given property with given name to properties. If allow_override is
        False, property will fail to add if it already exists. Otherwise specified prop will
        be updated via a call to update_property. Return success"""
        #if name not in self.properties:
        self.properties[name] = prop
        # Finalize property
        self.properties[name].finalize(self)

        return True

        #elif allow_override:
        #    return self.update_property(name, prop.get_pure_value())

        #return False

    def handle_component(self, events):
        """Handles own events and renders self"""
        if not self._disable_component:
            if not self._disable_interaction:
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

    def get_surface(self) -> Optional[pygame.Surface]:
        """
        Return the component's surface, and ensure it adheres to width and height.
        Override this method to add more property enforcers, but be sure to call this
        parent method to ensure width and height are always enforced
        """
        if self._disable_component:
            return None

        # Checks if surface conforms to height and width properties
        elif self._surface.get_height() == int(self.properties["height"].get_value()) and \
                self._surface.get_width() == int(self.properties["width"].get_value()):

            return self._surface

        # Returns resized surface otherwise
        return pygame.transform.smoothscale(self._surface, (self.properties["width"].get_value(),
                                                            self.properties["height"].get_value()))

    def disable_interaction(self):
        self._disable_interaction = True

    def enable_interaction(self):
        self._disable_interaction = False

    def disable_component(self):
        self._disable_component = True

    def enable_component(self):
        self._disable_component = False

    def is_disabled(self) -> bool:
        return self._disable_component


class Container(Component):
    """
    A component which can have children
    """
    def __init__(self, **kwargs: Property):
        Component.__init__(self, **kwargs)

        self._children = set()

    def add_child(self, child) -> None:
        """Set child's parent to self and add child to children.
        Makes sure the component is finalized"""
        child.parent = self
        child.finalize()
        self._children.add(child)

    def remove_child(self, child) -> bool:
        """Kill the child and return whether the murder was a success.
        I am just a function, I am just following orders."""
        if child in self._children:
            self._children.remove(child)
            return True
        return False

    def get_children(self) -> set[Component]:
        return self._children

    def handle_component(self, events):
        """Renders component as well as its children, and also calls event handlers"""
        Component.handle_component(self, events)

        if not self._disable_component:
            for child in self._children:

                # Handles component for each child
                child.handle_component(events)

                # Draws child surface relative to container surface. child surf is None if disabled
                child_surf = child.get_surface()
                if child_surf is not None:
                    self._surface.blit(child.get_surface(), (child.properties["left"].get_value(),
                                                             child.properties["top"].get_value()))

    def render_component(self):
        raise NotImplementedError


class WindowComponent(Container):
    """
    Stores the main pygame window
    """
    def __init__(self, width: int, height: int, background_color=(0, 0, 0)):
        # Window is a container with no parents
        Container.__init__(self,
                           width=NumericProperty(width),
                           height=NumericProperty(height),
                           background_color=Property(background_color))
        self.finalize()

    def generate_surface(self):
        return pygame.display.set_mode((int(self.properties["width"].get_value()),
                                        int(self.properties["height"].get_value())))

    def render_component(self):
        # Clears surface with a fill
        self._surface.fill(self.properties["background_color"].get_value())
