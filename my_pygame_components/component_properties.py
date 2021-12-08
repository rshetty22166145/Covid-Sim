from __future__ import annotations
from typing import Optional, Any
import my_pygame_components.component as comp
import logging


class Property:
    """
    Stores a GUI Component property

    Attributes:
        - value: Value of this property
        - name: String name of the property
        - component: Component to which this property belongs
    """
    def __init__(self, value: Any, component: Optional[comp.Component] = None):
        self._value = value
        self._component = component

    def finalize(self, component):
        self._component = component

    def update_value(self, new_value: Any) -> bool:
        """Update value as long as new_value is the same type"""
        if isinstance(new_value, type(self._value)):
            self._value = new_value
            return True
        return False

    def get_value(self):
        return self._value

    def get_pure_value(self):
        """In some subclasses, get_value might have some additional calculations
        This method always returns the pure original value of self._value"""
        return self._value

    def __str__(self):
        return str(self.get_value())

    def __repr__(self):
        return str(self.get_value())


class NumericProperty(Property):
    """
    Numerical Properties. If a property is relative, it must specify the parent property
    to take from

    Representation Invariants:
        - self.is_relative == False or self.relative_prop_name is not None

    Attributes:
        - is_relative: It this property a proportion of a parent property
        - relative_prop_name: The name of the numerical parent property to calculate from
    """
    def __init__(self, value: float, component: Optional[comp.Component] = None,
                 is_relative=False, relative_prop_name: Optional[str] = None):
        logging.info("NumericalProperty created with value " + str(value))
        Property.__init__(self, value, component)
        self._value = float(self._value)

        self._is_relative = is_relative
        self._relative_prop_name = relative_prop_name
        self._calculated_value = None if self._component is None else self._calculate_value()

    def finalize(self, component):
        Property.finalize(self, component)
        self._calculated_value = self._calculate_value()

    def _calculate_value(self):
        """
        Take the component to which this property belongs and compute
        the final value of this property given relativity
        """
        if not self._is_relative:
            return self._value
        else:
            # Goes up the parent tree of components until it finds a number to relate to
            c = self._component
            property_val = None

            while c.parent is not None:
                c = c.parent

                # If property exists and its numerical, calculate its value
                if self._relative_prop_name in c.properties and \
                        isinstance(c.properties[self._relative_prop_name], NumericProperty):

                    property_val = c.properties[self._relative_prop_name].get_value()
                    break

            # If the while loop tree trace found no ancestor with the prop, raise error
            if property_val is None:
                raise ParentPropNotFound
            else:
                # Returns value with proportion applied (self._value would be a proportion)
                return self._value * property_val

    def update_value(self, new_value: float) -> bool:
        """Updates value and recalculates"""
        if Property.update_value(self, new_value):
            self._calculated_value = self._calculate_value()
            return True
        return False

    def get_value(self):
        return self._calculated_value


class ParentPropNotFound(Exception):
    def __str__(self):
        return "Could not find the specified parent property to calculate from"
