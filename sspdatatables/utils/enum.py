"""
Module for defining the MappingEnum class and ConvertMappingEnum class.
"""
from named_enum import NamedEnum


class MappingEnum(NamedEnum):
    """
    Extends enumeration class with three attributes: `col_idx`, `order_key`,
    `filter_key` and checks each element in the value of each the enumeration
    item is a specific data type value.
    """
    _field_names_ = ['col_idx', 'order_key', 'filter_obj']

    def __init__(self, *args):
        """
        Doing the checks for the data type of the each element in the value of
        the enumeration item, make sure the `col_idx` is int type, `order_key`
        is a string and the `filter_obj` is either a 2-element tuple or a
        string.

        :param args: tuple: 3-element tuple, it's the value of the enumeration.
        """
        # force the user to define the mapping in a particular format
        if not isinstance(self.col_idx, int):
            raise TypeError("Parameter(s) '%s' must be %s." %
                            ("col_idx", "int value"))
        elif not isinstance(self.order_key, str):
            raise TypeError("Parameter(s) '%s' must be %s." %
                            ("order_key", "str value"))
        if isinstance(self.filter_obj, tuple) and len(self.filter_obj) != 2:
            raise TypeError("Parameter(s) '%s' must be %s." %
                            ("filter_obj", "a 2-element tuple or str value"))
        elif not isinstance(self.filter_obj, str):
            raise TypeError("Parameter(s) '%s' must be %s." %
                            ("filter_obj", "a 2-element tuple or str value"))


class ConvertMappingEnum(NamedEnum):
    """
    Customized Enum class for defining the conversion mapping for extracting
    and converting necessary parameter from request's QueryDict.

    The syntax defines the keys in the QueryDict, the default_val is the
    default value for the conversion
    """
    _field_names_ = ['syntax', 'default_val']

