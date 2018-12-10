from enum import Enum
from .utils.enum import ConvertMappingEnum


class SearchArea(Enum):
    """
    Enumeration for defining the relative position of the filter to the table.
    """
    No = 0  # means no filters for the table
    Header = 1  # means the filters are in the header of the table
    Footer = 2  # means the filters are in the footer of the table
    Customize = 3  # means the filters are in a customized container


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
