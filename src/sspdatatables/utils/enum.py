"""
Abstract Enumeration class and its subclass which defines an enumeration with
three elements
"""
from enum import Enum
from functools import partial, update_wrapper


class AbstractEnum(Enum):
    """
    This class was thought to work as an abstract class to simplify the
    definition of the enumeration classes with more than 1 attributes.
    """
    def __init__(self, attributes):
        """
        Abstract initial function to get a list of pairs in which defines the
        name and the value of the class variable. According to the attribute
        names in attributes, this function will create some function for its
        subclasses.
        For example, its subclass has attributes 'key' and 'value', then this
        function will create the functions 'keys', 'values', 'from_key',
        'from_value'.
        'keys' function returns a tuple containing all the values  of the
        attribute 'key'.
        'values' function returns a tuple containing all the values  of the
        attribute 'value'.
        'from_key' function returns the enumeration item containing the given
        value as key
        'from_value' function returns the enumeration item containing the given
        value as value

        :param attributes: dict/mapping/iterable objects: defines the
          attribute's name and value.
        """
        self.attr_names = []
        # uses the dict conversion to check if the parameter attributes is a
        # kind of mapping
        try:
            name_value_dict = dict(attributes)
        except Exception:
            print(Exception)
            raise ValueError("Invalid data type of parameter attributes.")
        for attr_name, attr_value in name_value_dict.items():
            # set up the attribute first
            setattr(self, attr_name, attr_value)
            self.attr_names.append(attr_name)
            # set up the function returning all the attributes
            setattr(self.__class__, attr_name + 's',
                    partial(self._attributes, attr_name))
            # override the docstring of the partial function
            update_wrapper(getattr(self.__class__, attr_name + 's'), self._attributes)
            # set up the function for extracting the given value in the
            # specific attribute
            setattr(self.__class__, 'from_' + attr_name,
                    partial(self._from_attr, attr_name))
            update_wrapper(getattr(self.__class__, 'from_' + attr_name), self._attributes)

    @classmethod
    def _attributes(cls, attr_name):
        """
        Returns a tuple containing just the valyue of the given attr_name of all
        the elements.

        :return: tuple of different types
        """
        return tuple(map(lambda x: getattr(x, attr_name), list(cls)))

    @classmethod
    def _from_attr(cls, attr_name, attr_value):
        """
        Returns the enumeration item regarding to the attribute name and value,
        or None if not found

        :param attr_name: str: attribute's name
        :param attr_value: different values: key to search for
        :return: different types, label associated to the given key
        """
        return next(iter(filter(lambda x: getattr(x, attr_name) == attr_value,
                                list(cls))), None)

    @classmethod
    def tuples(cls):
        """
        Returns a tuple formed by attributes for all the elements inside the
        class

        :return: tuple of n-elements-tuples
        """
        return tuple(cls._value2member_map_.keys())


class TripleEnum(AbstractEnum):
    """
    Extended enumeration class: implements some methods to work with tuples
    formed by a key, a label and an extra information in the format:
    FOO = (int, foo, extra).

    This class was thought to work with triples required by Django models and
    define a simple method to generate them and compare them.
    """
    def __init__(self, key, label, extra):
        """
        This init method is called when an attribute for the class
        is defined; therefore, the main class does not require to
        define key, label and extra manually. This is because each
        Attribute defined in the class calls this init with the parameters
        defined in the tuple. Therefore, each defined attribute is also a
        class.

        :param key: str/int: it's the key of the enumeration, so it must
            be unique
        :param label: str: the description of the key
        :param extra: str: the extra description of the key
        """
        super(TripleEnum, self).__init__(
            attributes=[("key", key), ("label", label), ("extra", extra)])

    def __str__(self):
        """
        String representation of the given enumeration. By default it
        returns the string conversion of the key associated to a value

        :return: str
        """
        return str(self.key)

    @classmethod
    def describe(cls):
        """
        Prints in the console a table showing the key, the label and the extra
        of all the definitions inside the class

        :return: None
        """
        key_list = list(map(str, cls.keys())) + ["Key"]

        max_ = max(list(map(len, key_list)))
        if max_ < 2:
            max_ = 2
        row_format = "{:>" + str(max_) + "}" + " | {:} | {:}"
        headers = ["Key", "Label", "Extra"]
        print("Class: ", cls.__name__)
        header_line = row_format.format(*headers)
        print(header_line)
        print("-"*(len(header_line)-1))

        for item in cls:
            print(row_format.format(str(item.key), item.label, item.extra))
