from typing import Optional, Any
from component import Component


class Property:
    """
    Stores a GUI Component property

    Attributes:
        - value: Value of this property
        - name: String name of the property
        - component: Component to which this property belongs
    """
    def __init__(self, value: Any, component: Optional[Component] = None):
        self.__value = value
        self.__component = component

    def finalize(self, component):
        self.__component = component

    def update_value(self, new_value: Any) -> bool:
        """Update value as long as new_value is the same type"""
        if isinstance(new_value, type(self.__value)):
            self.__value = new_value
            return True
        return False

    def get_value(self):
        return self.__value


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
    def __init__(self, value: float, component: Optional[Component] = None,
                 is_relative=False, relative_prop_name: Optional[str] = None):
        Property.__init__(self, value, component)
        self.__value = float(self.__value)

        self.__is_relative = is_relative
        self.__relative_prop_name = relative_prop_name
        self.__calculated_value = None if self.__component is None else self.__calculate_value()

    def finalize(self, component):
        Property.finalize(self, component)
        self.__calculate_value()

    def __calculate_value(self):
        """
        Take the component to which this property belongs and compute
        the final value of this property given relativity
        """
        if not self.__is_relative:
            return self.__value
        else:
            # Goes up the parent tree of components until it finds a number to relate to
            c = self.__component
            property_val = None

            while c.parent is not None:
                c = c.parent

                # If property exists and its numerical, calculate its value
                if self.__relative_prop_name in c.properties and \
                        isinstance(c.properties[self.__relative_prop_name], NumericProperty):

                    property_val = c.properties[self.__relative_prop_name].calculate_value(c)
                    break

            # If the while loop tree trace found no ancestor with the prop, raise error
            if property_val is None:
                raise ParentPropNotFound
            else:
                # Returns value with proportion applied (self.__value would be a proportion)
                return self.__value * property_val

    def update_value(self, new_value: Any) -> bool:
        """Updates value and recalculates"""
        if Property.update_value(self, new_value):
            self.__calculated_value = self.__calculate_value()
            return True
        return False

    def get_value(self):
        return self.__calculated_value


class ParentPropNotFound(Exception):
    def __str__(self):
        return "Could not find the specified parent property to calculate from"
