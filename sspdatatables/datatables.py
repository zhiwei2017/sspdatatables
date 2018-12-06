"""
Abstract Class for using `DataTables <https://datatables.net/>`_ package with
server side processing function in Django project.
"""
from .utils.data_type_ensure import ensure
from .utils.enum import TripleEnum
from collections import OrderedDict, defaultdict
from rest_framework.serializers import ModelSerializer
from .forms import AbstractFilterForm
from .constants import SearchArea, ConvertMapping, ConvertMappingColumn


__all__ = ['DataTables']


# defines the error messages used in DataTablesMeta class and DataTables Class
# for the checking
_error_msg = {
    "undefined_meta": "Class 'Meta' isn't defined.",
    "wrong_type_meta": "Class 'Meta' isn't defined as a nested class.",
    "missing_attr": "Variable(s) %r must be defined in Meta class.",
    "none_attr": "{Variable(s)} %r can not be None.",
    "wrong_data_type": "Variable/Parameter(s) '%s' must be %s.",
    "missing_k_in_frame": "Key(s) %r are missing",
    "none_form": "Variable 'form' can not be None, if filter_type is not input",
    "invalid_filter_k": "Invalid filter key.",
    "invalid_attr_in_query_dict": "Parameter 'query_dict' contains non-existent"
                                  " attribute.",
    "unorderable_column": "The column [%d] is unorderable."
}


class DataTablesMeta(type):
    """
    Simple meta class to check if a subclass of `DataTables` defines a nested
    `Meta` class, and inside the `Meta` class the variables:
    `serializer`, `frame`, `mapping`, `form`, `search_area` are defined as
    requisite data type.
    """
    def __new__(mcs, name, bases, namespace):
        """
        Used for defining the Meta class's structure and check it when creating
        a subclass's instance, such that the user will be forced to follow the
        rules as following:

        1. serializer: must be defined as a subclass of ModelSerializer

        2. frame: must be defined as a list of dictionary, each
        dictionary has the following structure:

            - "header": "<Header to display>",
            - "searchable": <bool value to set the columns to be searchable or
            not, True/False>,
            - "orderable": <bool value to set the columns to be orderable
            - or not, True/False>,
            - "filter_type": type of the footer search bar, input/select,
            - "id": "<id of this footer search bar, together with parameter
            'prefix' to build the id>",
            - "serializer_key": "<key to extract the data from the serialized
            data set>"

        3. form: must be defined if there is at least one footer whose type is
        not 'input'

        4. mapping: must be defined in the following format:
            ```
            class COL_TRIPLE_ENUM(TripleEnum):
                A = ("<position of the column>", "<corresponding order key
                 name>", "<corresponding filter key>")
            ```
        It's the key to get the correct data from DB

        :return: class instance
        """
        cls = super().__new__(mcs, name, bases, namespace)
        # the class 'DataTables' doesn't need any further checks
        if not bases:
            return cls

        # each subclass of class 'DataTables' must define the nested Meta class
        # for defining requisite variables
        if "Meta" not in namespace:
            raise AttributeError(_error_msg["undefined_meta"])
        _meta = getattr(cls, "Meta")
        # make sure the Meta is a nested class
        if not isinstance(_meta, type):
            raise AttributeError(_error_msg["wrong_type_meta"])

        # checks the Meta class contains the definitions of variables:
        # 'serializer', 'frame', 'mapping'
        meta_attrs = {"serializer", "frame", "mapping"}
        missing_attrs = meta_attrs.difference(_meta.__dict__.keys())
        if missing_attrs:
            raise AttributeError(
                _error_msg["missing_attr"] % list(missing_attrs))
        # checks the variables are not None
        none_attrs = [attr_name for attr_name in meta_attrs
                      if getattr(_meta, attr_name) is None]
        if none_attrs:
            raise AttributeError(_error_msg["none_attr"] % none_attrs)

        # serializer should be a subclass of ModelSerializer from rest_framework
        serializer = getattr(_meta, "serializer")
        if not issubclass(serializer, ModelSerializer):
            raise TypeError(_error_msg["wrong_data_type"]
                            % 'serializer', "a subclass of ModelSerializer.")

        # form can be None, if the user doesn't user footer or uses input field
        # as footer. Otherwise, it must be defined as a subclass of
        # AbstractFilterForm
        if not hasattr(_meta, "form"):
            _meta.form = None
        elif _meta.form and not issubclass(_meta.form, AbstractFilterForm):
            raise ValueError(
                _error_msg["wrong_data_type"] % 'form',
                "a subclass of AbstractFilterForm or None")

        # frame should be a list of dictionaries and in each dictionary some
        # keys must be contained.
        frame = getattr(_meta, "frame")
        must_have_keys = {"id", "serializer_key", "header", "searchable",
                          "orderable", "filter_type"}
        if not isinstance(frame, list) or not frame:
            raise ValueError(_error_msg["wrong_data_type"]
                             % 'frame', "a nonempty list of dictionaries.")
        for item in frame:
            if not isinstance(item, dict):
                raise ValueError(_error_msg["wrong_data_type"]
                                 % 'frame', "a nonempty list of dictionaries.")
            missing_keys = must_have_keys.difference(item.keys())
            if missing_keys:
                raise ValueError(
                    _error_msg["missing_k_in_frame"] % list(missing_keys))
            if item["filter_type"] not in {"input", None} and not _meta.form:
                raise ValueError(_error_msg["none_form"])

        # mapping must be a subclass of TripleEnum class
        mapping = getattr(_meta, "mapping")
        if not issubclass(mapping, TripleEnum):
            raise ValueError(_error_msg["wrong_data_type"]
                             % "mapping", "a subclass of TripleEnum.")
        # force the user to define the mapping in a particular format
        # TODO: use the named enum
        for item in list(mapping):
            if not isinstance(item.key, int):
                
                raise TypeError(
                    _error_msg["wrong_data_type"] % "key", "int value")
            elif not isinstance(item.label, str):
                raise TypeError(
                    _error_msg["wrong_data_type"] % "label", "str value")
            if isinstance(item.extra, tuple) and len(item.extra) != 2:
                raise TypeError(
                    _error_msg["wrong_data_type"] % "extra",
                    "a 2-element tuple or str value")
            elif not isinstance(item.extra, str):
                raise TypeError(
                    _error_msg["wrong_data_type"] % "extra",
                    "a 2-element tuple or str value")

        # the search_area must be one of the enumerations, it's optional
        if not hasattr(_meta, "search_area"):
            _meta.search_area = SearchArea.No
        elif not isinstance(_meta.search_area, SearchArea):
            raise ValueError(_error_msg["wrong_data_type"]
                             % 'search_area', "the element of Enum SearchArea")

        cls._meta = _meta
        return cls


class DataTables(metaclass=DataTablesMeta):
    """
    This class aims to simplify the process of using package
    `DataTables <https://datatables.net/>`_'s server-side processing function
    in a django project.

    It uses a nested `Meta` class to define the requisite attributes:

    * `serializer`: a `ModelSerializer` class (using `DjangoRestFramework
      <https://www.django-rest-framework.org/>`_ package)
    * `form`: a normal Django `Form`, which defines the choice fields for the
      filter. An abstract dynamical form is provided in **forms.py**.
    * `frame`: a `list` of dictionaries, defines the table's frame
    * `mapping`: `TripleEnum` class, which indicates the mapping between column
      position, corresponding order key and corresponding filter key.
    * `search_area`: `SearchArea` enumeration, indicates where the filters
    locate

    Besides the `Meta` class, the functions: `_get_filter_dict`,
    `_get_order_key`, `_filtering`, `_slicing`, `_query_by_args`, can be
    customized by the user according to some specific use cases.

    The user can also customize the behavior of the `DataTables` class by
    defining a customized initial function.
    """
    serializer = property(lambda self: self.Meta.serializer)
    """Wrapper to render the `serializer` in `Meta` class. It provides the 
    opportunity to use one `DataTables` class with different serializers."""

    form = property(lambda self: self.Meta.form)
    """Wrapper to render the `form` in `Meta` class. It provides the opportunity
     to use one `DataTables` class with different forms"""

    frame = property(lambda self: self.Meta.frame)
    """wrapper to render the `frame` in `Meta` class. It provides the 
    opportunity to use one `DataTables` class with different frames"""

    mapping = property(lambda self: self.Meta.mapping)
    """Wrapper to render the `mapping` in `Meta` class. It provides the 
    opportunity to use one `DataTables` class with different mappings."""

    search_area = property(lambda self: self.Meta.search_area.value)
    """Wrapper to render the value of `search_area` in `Meta` class, it provides
     the opportunity to work with different mappings."""

    def _filter_form(self, *args, **kwargs):
        """
        Creates an instance of the filter form.

        This function can be customized for the complicated use case.

        :param args: list: args for the filter form initialization
        :param kwargs: dict: args for the filter form initialization
        :return: Django Form instance
        """
        return self.form(*args, **kwargs)

    def get_table_frame(self, prefix="", table_id="sspdtable", *args, **kwargs):
        """
        Renders the id, the frame and the initialized filter form of the table.

        :param prefix: str: used for specializing the rendered parameter's name,
          such that the template of the package can be used in one page for
          multiple times.
        :param table_id: str: id of the table in html
        :param args: list: args for the footer form initialization
        :param kwargs: dict: args for the footer form initialization
        :return: dict
        """
        if not table_id:
            raise ValueError("table_id parameter can not be an empty string.")
        table_key = prefix + "sspdtable"
        context = {
            table_key: {
                "id": table_id,
                "frame": self.frame,
                "search_area": self.search_area,
            }
        }
        if self.form:
            context[table_key]['footer_form'] = self._filter_form(*args,
                                                                  **kwargs)
        return context

    def _get_filter_dict(self, **query_dict):
        """
        Generates a filter dictionary, in which the key is the filter key in
        django queryset's `filter` function in form of string, and the value is
        the searched value.

        :param query_dict: dict: dictionary contains the necessary parameter for
          generating the filter dictionary.
        :return: dict: filtering dictionary, which can be used directly in the
          `filter` function.
        """
        filter_dict = defaultdict(dict)
        for column_idx, search_value in query_dict["columns"]:
            # through the column index to get corresponding the enumeration item
            # from the class's mapping variable
            enum_item = self.mapping.from_key(column_idx)
            filter_obj = enum_item.extra
            # if the filter_obj is a tuple and the length of the tuple is 2, we
            # take the first element of the tuple as the customized filter
            # function and the second element as the search value.
            # This is used, when the user customized the queryset manager or the
            # model manager.
            if isinstance(filter_obj, tuple) and len(filter_obj) == 2:
                filter_func, filter_key = filter_obj
                filter_dict[filter_func][filter_key] = search_value
            # if it's a string, then use it as the seach value of the default
            # `filter` function.
            elif isinstance(filter_obj, str):
                filter_dict['filter'][filter_obj] = search_value
            # for the other case, directly raise an error.
            else:
                raise ValueError(_error_msg["invalid_filter_k"])
        return filter_dict

    def _get_order_key(self, **query_dict):
        """
        Gets the order key and order direction from the query dictionary.

        :param query_dict: dict: converted query dict from request
        :return: str: order direction + key, which can be used directly in
          queryset's `order_by` function.
        """
        order_column = query_dict[ConvertMapping.order_by.name]
        order_key = self.mapping.from_key(order_column).label
        order_key = query_dict[ConvertMapping.order_direction.name] + order_key
        return order_key

    @staticmethod
    def _filtering(queryset, filter_dict):
        """
        Applies the filter conditions defined the `filter_dict` to the
        `queryset`.

        :param queryset: Django Queryset: queryset of all objects
        :param filter_dict: dict: contains selected_related, filter and other
          customized filter functions
        :return: queryset: result after applying the pre search condition dict
        """
        # apply pre_search_condition
        for key, value in filter_dict.items():
            # if the function is undefined in the queryset manager, raise an
            # error.
            if not hasattr(queryset, key):
                raise AttributeError(
                    _error_msg["invalid_attr_in_query_dict"])
            elif isinstance(value, list):
                queryset = getattr(queryset, key)(*value)
            elif isinstance(value, dict):
                queryset = getattr(queryset, key)(**value)
            else:
                queryset = getattr(queryset, key)(value)
        return queryset

    def _ordering(self, queryset, **query_dict):
        """
        Orders the queryset by the order key generated from query_dict.

        :param queryset: Django Queryset: queryset of all objects
        :param query_dict: dict: converted query dict from request
        :return: queryset: result after applying the pre search condition dict
        """
        order_key = self._get_order_key(**query_dict)
        queryset = queryset.order_by(order_key)
        return queryset

    @staticmethod
    def _slicing(queryset, **query_dict):
        """
        Slices the queryset according to the display length.

        :param queryset: Django Queryset: filtered and ordered queryset result
        :param query_dict: dict: query dict sent by data tables package
        :return: queryset: result after _slicing
        """
        # if the length is -1, we need to display all the records
        # otherwise, just _slicing the queryset
        length = query_dict[ConvertMapping.length.name]
        start = query_dict[ConvertMapping.start.name]
        if length >= 0:
            queryset = queryset[start:start + length]
        return queryset

    def _query_by_args(self, pre_search_condition=None, **query_dict):
        """
        Intends to process the queries sent by data tables package in frontend.
        The model_cls indicates the model class, _get_filter_dict is a function
        implemented by you, such that it can
        return a query dictionary, in which the key is the query keyword in str
        form and the value is the queried value

        :param pre_search_condition: None/OrderedDict: dictionary contains
          filter conditions which should be processed before applying the filter
          dictionary from user. None, if no pre_search_condition provided.
        :param query_dict: QueryDict: contains query parameters
        :return: dict: contains total records number, queryset of the filtered
          instances, size of this queryset
        """
        if pre_search_condition and not isinstance(pre_search_condition,
                                                   OrderedDict):
            raise TypeError(
                _error_msg["wrong_data_type"] % 'pre_search_condition',
                "an OrderedDict")

        # just implement the _get_filter_dict function
        filter_dict = self._get_filter_dict(**query_dict)

        # get the model from the serializer parameter
        model_class = self.serializer.Meta.model
        # get the objects
        queryset = model_class.objects

        # apply the pre search condition if it exists
        if pre_search_condition:
            queryset = self._filtering(queryset, pre_search_condition)
        else:
            queryset = queryset.all()

        # number of the total records
        total = queryset.count()

        # if the query dict not empty, then apply the query dict
        if filter_dict:
            queryset = self._filtering(queryset, filter_dict)

        # number of the records after applying the query
        count = queryset.count()

        # order the queryset
        queryset = self._ordering(queryset, **query_dict)

        # slice the queryset
        queryset = self._slicing(queryset, **query_dict)
        return {'items': queryset, 'count': count, 'total': total,
                'draw': query_dict['draw']}

    def _convert_query_dict(self, query_dict):
        """
        Converts the QueryDict of the request to a dictionary, in which the keys
        and values are more understandable and directly usable.

        :param query_dict: QueryDict: dictionaries contained in the request
        :return: dictionary contains the necessary parameters and nonempty
          search values.
        """
        # the final converted dictionary
        converted_dict = {}

        # first convert the the parameters for the whole table
        for name, value in ConvertMapping.gen():
            item = query_dict.get(value.syntax, [value.default_val])
            item = next(iter(item))
            item = ensure(type(value.default_val), item, value.default_val)
            data_type = type(value.default_val)
            converted_dict[name] = ensure(data_type, item, value.default_val)
        # for the order direction parameter, convert it to match the django
        # format, such that it can be used in the order_by function of the
        # queryset
        order_direction = ConvertMapping.order_direction.name
        is_desc = converted_dict[order_direction] == "desc"
        converted_dict[order_direction] = "-" * is_desc

        # dictionary to hold the search value for each column temporary
        search_value_dict = dict()
        # the first column number to iterate
        starter = next(iter(self.mapping.keys()))
        # iterates every column to get the filter values and check if the column
        # used for ordering is really orderable.
        # The logic is :
        # 1. if the search value is empty, skip this column
        # 2. if the column is not searchable, skip this column
        # 3. if this column is nonorderable and used for ordering, raise error
        # 4. for the rest cases, store the search value in the dictionary
        for i in range(starter, converted_dict[ConvertMapping.total_cols.name]):
            temp = dict()
            # firstly extracts the columns's search value, searchable and
            # orderable values and convert the searchable and orderable values
            # to boolean value preparing for the next step
            for name, value in ConvertMappingColumn.gen():
                syntax = value.syntax.format(index=i)
                item = query_dict.get(syntax, [value.default_val])
                item = next(iter(item))
                item = item.strip()
                temp[name] = item
            # if the search value of this column is empty, skip
            if not temp[ConvertMappingColumn.search_value.name]:
                continue
            # if this column is not searchable, skip
            elif temp[ConvertMappingColumn.searchable.name] != 'true':
                continue
            # if a nonorderable column is used for ordering, raise error
            elif converted_dict[ConvertMapping.order_by.name] == i \
                    and temp[ConvertMappingColumn.orderable.name] != 'true':
                raise ValueError(_error_msg["unorderable_column"] % (i+1))
            # store the search value in the dictionary
            search_value_dict[i] = temp[ConvertMappingColumn.search_value.name]
        # store the nonempty search values of the columns as generator.
        converted_dict["columns"] = (item for item in search_value_dict.items())
        return converted_dict

    def process(self, pre_search_condition=None, **kwargs):
        """
        Applies the filter condition from the webpage to the DB and renders the
        serialized result.

        :param pre_search_condition: None/OrderedDict: pre search condition to
          be applied before applying the one getting from footer
        :param kwargs: dict: search parameters got from footer
        :return: dict: contains the filtered data, total number of records,
            number of filtered records and drawing number.
        """
        query_dict = self._convert_query_dict(kwargs)
        records = self._query_by_args(pre_search_condition=pre_search_condition,
                                      **query_dict)
        serializer = self.serializer(records['items'], many=True)
        result = {
            'data': serializer.data,
            'draw': records['draw'],
            'recordsTotal': records['total'],
            'recordsFiltered': records['count'],
        }
        return result
