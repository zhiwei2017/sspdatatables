from sspdatatables.utils.enum import MappingEnum


class BookEnum(MappingEnum):
    """
    class to define a mapping
    """
    ID = (1, "id", "id")
    NAME = (2, "name", "name__icontains")
    AUTHOR_NAME = (3, "author__name", "author__name__icontains")
    AUTHOR_NATIONALITY = (4, "author__nationality", "author__nationality")
    PUBLISHED_AT = (5, "published_at", "published_at")