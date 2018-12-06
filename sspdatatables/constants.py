from enum import Enum
from named_enum import NamedEnum


class SearchArea(Enum):
    """
    Enumeration for defining the relative position of the filter to the table.
    """
    No = 0  # means no filters for the table
    Header = 1  # means the filters are in the header of the table
    Footer = 2  # means the filters are in the footer of the table
    Customize = 3  # means the filters are in a customized container


class ConvertMappingEnum(NamedEnum):
    """
    Customized Enum class for defining the conversion mapping for extracting
    and converting necessary parameter from request's QueryDict.

    The syntax defines the keys in the QueryDict, the default_val is the
    default value for the conversion
    """
    _field_names_ = ['syntax', 'default_val']


class ConvertMapping(ConvertMappingEnum):
    """
    Mapping for converting the parameters for the whole table
    """
    draw = ("draw", 0)
    total_cols = ("total_cols", 0)
    length = ("length", 0)
    start = ("start", 0)
    order_by = ("order[0][column]", 1)
    order_direction = ("order[0][dir]", "asc")


class ConvertMappingColumn(ConvertMappingEnum):
    """
    Mapping for converting the parameters for each column.
    """
    searchable = ("columns[{index}][searchable]", "false")
    orderable = ("columns[{index}][orderable]", "false")
    search_value = ("columns[{index}][search][value]", "")