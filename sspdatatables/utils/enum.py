"""
Module for the classes extending the default Enum class. It contains 3 classes:
ExtendedEnumMeta, ExtendedEnum, TripleEnum.
"""
from enum import Enum, EnumMeta
from functools import partial
from typing import Tuple, Any, Dict, List, TypeVar


class ExtendedEnumMeta(EnumMeta):
    """
    Meta class to extend the EnumMeta class with several functions according to
    the returned result of the class method 'attr_names' in Enumeration class.
    It will create two kind of functions for each attr_name:
    1. returns the collective results of the same attr_name from all
      enumerations of the same Enumeration class
    2. returns the enumeration according to the given value of the specific
      attr_name
    """
    def __new__(mcs, name: str, bases: Tuple[type, ...],
                namespace: Dict[str, Any]) -> type:
        """
        Intends to create the functions with name formats:
        <attr_name>s and from_<attr_name>
        for each attr_name in the result of class method 'attr_names' in its
        instance classes

        :param name: str: name of the instance class
        :param bases: tuple: base classes, its instance class inherits from
        :param namespace: dict: contains the attributes and functions of the
          instance class
        :return: class object
        """
        cls = super().__new__(mcs, name, bases, namespace)
        func_name_and_doc = [
            ("%ss",
             "Collective function to return the values of the attribute %s from"
             " all the enumerations in the Enum class.",
             mcs._attrs_),
            ("from_%s",
             "Returns the corresponding enumeration according to the given "
             "value of the attribute %s.",
             mcs._from_attr_)
        ]
        for attr_name in cls.attr_names():
            for name, docstring, meta_func in func_name_and_doc:
                func_name = name % attr_name
                func_docstring = docstring % attr_name
                setattr(cls, func_name, partial(meta_func, cls, attr_name))
                # override the docstring of the partial function
                getattr(cls, func_name).__doc__ = func_docstring
        return cls

    @classmethod
    def _attrs_(mcs, cls, attr_name: str) -> Tuple[Any, ...]:
        """
        Returns a tuple containing just the value of the given attr_name of all
        the elements from the cls.

        :return: tuple of different types
        """
        return tuple(map(lambda x: getattr(x, attr_name), list(cls)))

    @classmethod
    def _from_attr_(mcs, cls, attr_name: str, attr_value: Any) -> TypeVar:
        """
        Returns the enumeration item regarding to the attribute name and value,
        or None if not found for the given cls

        :param attr_name: str: attribute's name
        :param attr_value: different values: key to search for
        :return: Enumeration Item
        """
        return next(iter(filter(lambda x: getattr(x, attr_name) == attr_value,
                                list(cls))), None)


class ExtendedEnum(Enum, metaclass=ExtendedEnumMeta):
    """
    This class was thought to work as an abstract class to simplify the
    definition of the enumeration classes with more than 1 attributes.
    """
    def __init__(self, *args, **kwargs) -> None:
        """
        Intends to assign the given values to attributes according to the order.

        :param args: list: values of the attributes of the enumeration item
        :param kwargs: dict: it should be empty
        """
        if len(kwargs):
            raise ValueError("The initialization of enumeration doesn't accept "
                             "key word arguments")
        attr_names = self.attr_names()
        if len(args) != len(attr_names):
            raise ValueError("The number of given values doesn't match the "
                             "number of defined attributes")
        for i, attr_name in enumerate(attr_names):
            setattr(self, attr_name, args[i])

    @classmethod
    def attr_names(cls) -> List[str]:
        """
        class method for defining the names of the attributes, it's used in two
        places:
        1. in the initial function of the class 'ExtendedEnum', the attributes
          will be set
        2. the meta class's __new__function to generate the corresponding
          functions for each attribute.

        :return: list of list of attribute names
        """
        return list()

    @classmethod
    def tuples(cls) -> Tuple[Tuple[Any, ...]]:
        """
        Returns a tuple formed by attributes for all the elements inside the
        class

        :return: tuple of n-elements-tuples
        """
        return tuple(cls._value2member_map_.keys())

    def __str__(self) -> str:
        """
        String representation of the given enumeration. By default it
        returns the string conversion of the first attribute from the attr_names
        associated to a value

        :return: str
        """
        return str(getattr(self, self.attr_names()[0]))

    @classmethod
    def describe(cls) -> None:
        """
        Prints in the console a table showing all the attributes for all the
        definitions inside the class

        :return: None
        """
        max_lengths = []
        for attr_name in cls.attr_names():
            attr_func = "%ss" % attr_name
            attr_list = list(map(str, getattr(cls, attr_func)())) + [attr_name]
            max_lengths.append(max(list(map(len, attr_list))))
        row_format = "{:>%d} | {:>%d} | {:>%d}" % tuple(max_lengths)
        headers = [attr_name.capitalize() for attr_name in cls.attr_names()]
        header_line = row_format.format(*headers)
        output = "Class: %s\n" % cls.__name__
        output += header_line + "\n"
        output += "-"*(len(header_line)) + "\n"
        for item in cls:
            format_list = [str(getattr(item, attr_name))
                           for attr_name in cls.attr_names()]
            output += row_format.format(*format_list) + "\n"
        print(output)


class TripleEnum(ExtendedEnum):
    """
    Extended enumeration class: implements some methods to work with tuples
    formed by a key, a label and an extra information in the format:
    FOO = (int, foo, extra).
    """
    @classmethod
    def attr_names(cls) -> List[str]:
        return ['key', 'label', 'extra']
