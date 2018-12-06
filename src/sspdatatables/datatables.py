"""
Abstract Class for using datatables package with server side processing option in Django project.
"""
from .utils.data_type_ensure import ensure
from .utils.enum import TripleEnum
from collections import OrderedDict, defaultdict
from typing import (
    Tuple, Any, Dict
)
from rest_framework.serializers import ModelSerializer
from .forms import AbstractFooterForm


class DataTablesMeta(type):
    """
    Simple meta class to check if a subclass of DataTables defines a nested Meta
    class and inside the Meta class the variables:
    'serializer', 'frame', 'mapping' (perhaps 'form')
    are defined as desired data type.
    """
    def __new__(mcs, name: str, bases: Tuple[type, ...],
                namespace: Dict[str, Any]) -> type:
        """
        Used for defining the Meta class's structure and check it when creating
        a subclass's instance,
        such that the user will be forced to follow the rules as following:
        1. serializer: must be defined as a subclass of ModelSerializer
        2. structure: must be defined as a list of dict, it should look like:
            [
                {
                    "header": "<Header to display>",
                    "searchable": <bool value to set the columns to be
                      searchable or not, True/False>,
                    "orderable": <bool value to set the columns to be orderable
                    or not, True/False>,
                    "footer_type": type of the footer search bar, input/select,
                    "id": "<id of this footer search bar, together with
                      parameter 'prefix' to build the id>",
                    "serializer_key": "<key to extract the data from the
                      serialized data set>"
                }
            ]
        3. structure_for_superuser: same as above
        4. form: must be defined if there is at least one footer whose type is
            not 'input'
        5. mapping: must be defined as the following structure:
            class COL_TRIPLE_ENUM(TripleEnum):
                A = ("<number of the column in frontend>", "<correspinding field
                 name>", "<corresponding filter key>")
            It's the key to get the correct data from DB

        :return: class instance
        """
        cls = super().__new__(mcs, name, bases, namespace)
        # the class 'DataTables' doesn't need any further checks
        if not bases:
            return cls

        # each subclass of class 'DataTables' must define the Meta class
        if "Meta" not in namespace:
            raise AttributeError("Class Meta isn't defined.")
        _meta = getattr(cls, "Meta")
        # make sure the Meta is a nested class
        if not isinstance(_meta, type):
            raise AttributeError("Meta isn't defined as a nested class.")

        # checks the Meta class contains the definitions of variables:
        #     serializer, frame, mapping
        meta_attrs = {"serializer", "frame", "mapping"}
        missing_attrs = meta_attrs.difference(_meta.__dict__.keys())
        if missing_attrs:
            raise AttributeError("Variable(s) %r must be defined in Meta class."
                                 % list(missing_attrs))
        # checks the variables are not None
        for attr_name in meta_attrs:
            if getattr(_meta, attr_name) is None:
                raise AttributeError(
                    "Variable '%s' can not be None." % attr_name)

        # serializer should be a subclass of ModelSerializer from rest_framework
        serializer = getattr(_meta, "serializer")
        if not issubclass(serializer, ModelSerializer):
            raise TypeError(
                "Variable 'serializer' must be a subclass of ModelSerializer.")

        # frame should be a list of dictionaries and in each dictionary some
        # keys must be contained.
        frame = getattr(_meta, "frame")
        must_have_keys = {"id", "serializer_key", "header", "searchable",
                          "orderable", "footer_type"}
        if not isinstance(frame, list):
            raise ValueError("Variable 'frame' must be a list of dictionaries.")
        elif not frame:
            raise ValueError("Variable 'frame' must not be empty.")
        for item in frame:
            if not isinstance(item, dict):
                raise ValueError("Variable 'frame' must be a list of "
                                 "dictionaries.")
            missing_keys = must_have_keys.difference(item.keys())
            if missing_keys:
                raise ValueError("Keys %r are missing" % list(missing_keys))

        # mapping must be a subclass of TripleEnum class
        mapping = getattr(_meta, "mapping")
        if not issubclass(mapping, TripleEnum):
            raise ValueError("Variable 'mapping' must inherit from class "
                             "TripleEnum.")

        # form can be None, if the user doesn't user footer or uses input field
        # as footer. Otherwise, it must be defined as a subclass of
        # AbstractFooterForm
        if not hasattr(_meta, "form"):
            _meta.form = None
        if not _meta.form:
            for item in frame:
                if item.get("footer_type") not in {"input", None}:
                    raise ValueError(
                        "If you don't use 'input' as your table's footer type, "
                        "please do not leave the form as None.")
        elif not issubclass(_meta.form, AbstractFooterForm):
            raise ValueError(
                "Variable 'form' must be defined as a subclass of "
                "AbstractFooterForm or None.")

        cls._meta = _meta
        return cls


class DataTables(metaclass=DataTablesMeta):
    """
    This class aims to simplify the process of using datatables's serverside option
    in a django project. It defines a similar structure like django ModelForm, using Meta
    class. Inside the Meta class, the user has to define couple things:
    * serializer: a ModelSerializer class (using rest_framework package)
    * form: a normal django from, which defines the choice fields for the footer.
    An abstract dynamical form is provided in forms.py file.
    * structure: list of dict, defines the table structure in frontend
    * structure_for_superuser: same as above, but for superuser
    * mapping: TripleEnum class, which holds the mapping between column number
    in frontend, corresponding field name in model class and corresponding key
    for filtering in DB
    Besides the Meta class, the functions, 'get_query_dict', 'query_by_args', can be
    customized by the user according to some specific use cases. The other functions are
    not necessary to be overridden.
    """
    serializer = property(lambda self: self.Meta.serializer)
    """Wrapper to render the serializer in Meta class, it provides a way to use
    one DataTables class with different serializers."""

    form = property(lambda self: self.Meta.form)
    """Wrapper to render the form in Meta class, it provides a way to use one 
    DataTables class with different forms"""

    frame = property(lambda self: self.Meta.frame)
    """wrapper to render the structure in Meta class"""

    mapping = property(lambda self: self.Meta.mapping)
    """Wrapper to render the mapping in Meta class, it provides a way
        to use one DataTables class with different mappings."""

    def footer_form(self, *args, **kwargs):
        """
        wrapper to render an instance of the footer form, which is the form in
        Meta class

        :param args: list: args for the footer form initialization
        :param kwargs: dict: args for the footer form initialization
        :return: form instance
        """
        return self.form(*args, **kwargs)

    def get_table_frame(self, prefix="", table_id="sspdtable", *args, **kwargs):
        """
        render the structure (or structure_for_superuser) and an instance of the
        footer form

        :param prefix: str: used for unifying the rendered parameter's name,
            such
            that the template of serverside datatables can be used in one page
            multiple times
        :param table_id: str:
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
                "frame": self.frame
            }
        }
        if self.form:
            context[table_key]['footer_form'] = self.footer_form(*args, **kwargs)
        return context

    def get_query_dict(self, **kwargs):
        """
        function to generate a filter dictionary, in which the key is the
        keyword used in django filter function in string form, and the value is
        the searched value.

        :param kwargs:dict: query dict sent by data tables package
        :return: dict: filtering dictionary
        """
        total_cols = ensure(int, kwargs.get('total_cols', [0])[0], 0)
        mapping = self.mapping
        filter_dict = defaultdict(dict)

        # set up the starter, since sometimes we start the enumeration from '1'
        starter = mapping.keys()[0]
        for i in range(starter, total_cols):
            key = 'columns[{index}]'.format(index=i)
            if kwargs.get(key + '[searchable]', [0])[0] != 'true':
                continue
            search_value = kwargs.get(key + '[search][value]', [''])[0].strip()
            if not search_value:
                continue
            enum_item = mapping.from_key(i)
            filter_obj = enum_item.extra
            if type(filter_obj) is tuple and len(filter_obj) == 2:
                filter_func, filter_key = filter_obj
                filter_dict[filter_func][filter_key] = search_value
            elif type(filter_obj) is str:
                filter_dict['filter'][filter_obj] = search_value
            else:
                raise ValueError("Invalid filter key.")
        return filter_dict

    def get_order_key(self, **kwargs):
        """
        function to get the order key to apply it in the filtered queryset

        :param kwargs: dict: query dict sent by data tables package
        :return: str: order key, which can be used directly in queryset's
          order_by function
        """
        # get the mapping enumeration class from Meta class
        mapping = self.mapping
        # use the first element in the enumeration as default order column
        order_column = kwargs.get('order[0][column]',
                                  [mapping.keys()[0]])[0]
        order_column = ensure(int, order_column, mapping.keys()[0])
        order = kwargs.get('order[0][dir]', ['asc'])[0]

        order_key = mapping.from_key(order_column).label
        # django orm '-' -> desc
        if order == 'desc':
            order_key = '-' + order_key
        return order_key

    @staticmethod
    def filtering(queryset, query_dict):
        """
        function to apply the pre search condition to the queryset to narrow
        down the queryset's size

        :param queryset: Django Queryset: queryset of all objects
        :param query_dict: dict: contains selected_related, filter and other
          customized filter functions
        :return: queryset: result after applying the pre search condition dict
        """
        # apply pre_search_condition
        for key, value in query_dict.items():
            assert hasattr(queryset, key), "Parameter 'query_dict' contains"\
                                           " non-existent attribute."
            if isinstance(value, list):
                queryset = getattr(queryset, key)(*value)
            elif isinstance(value, dict):
                queryset = getattr(queryset, key)(**value)
            else:
                queryset = getattr(queryset, key)(value)
        return queryset

    @staticmethod
    def slicing(queryset, **kwargs):
        """
        function to slice the queryset according to the display length

        :param queryset: Django Queryset: filtered and ordered queryset result
        :param kwargs: dict: query dict sent by data tables package
        :return: queryset: result after slicing
        """
        # if the length is -1, we need to display all the records
        # otherwise, just slicing the queryset
        length = ensure(int, kwargs.get('length', [0])[0], 0)
        start = ensure(int, kwargs.get('start', [0])[0], 0)
        if length >= 0:
            queryset = queryset[start:start + length]
        return queryset

    def query_by_args(self, pre_search_condition=None, **kwargs):
        """
        intends to process the queries sent by data tables package in frontend.
        The model_cls indicates the model class, get_query_dict is a function
        implemented by you, such that it can
        return a query dictionary, in which the key is the query keyword in str
        form and the value is the queried value

        :param pre_search_condition: None/OrderedDict: dictionary contains
          filter conditions which should be processed before applying the filter
          dictionary from user. None, if no pre_search_condition provided.
        :param kwargs: QueryDict: contains query parameters
        :return: dict: contains total records number, queryset of the filtered
          instances, size of this queryset
        """
        if pre_search_condition and not isinstance(pre_search_condition, OrderedDict):
            raise TypeError(
                "Parameter 'pre_search_condition' must be an OrderedDict.")
        # extract requisite parameters from kwargs
        draw = ensure(int, kwargs.get('draw', [0])[0], 0)

        # just implement the get_query_dict function
        query_dict = self.get_query_dict(**kwargs)
        order_key = self.get_order_key(**kwargs)

        # get the model from the serializer parameter
        model_class = self.serializer.Meta.model
        # get the objects
        queryset = model_class.objects

        # apply the pre search condition if it exists
        if pre_search_condition:
            queryset = self.filtering(queryset, pre_search_condition)
        else:
            queryset = queryset.all()

        # number of the total records
        total = queryset.count()

        # if the query dict not empty, then apply the query dict
        if query_dict:
            queryset = self.filtering(queryset, query_dict)

        # number of the records after applying the query
        count = queryset.count()

        # order the queryset
        queryset = queryset.order_by(order_key)

        # slice the queryset
        queryset = self.slicing(queryset, **kwargs)
        return {'items': queryset, 'count': count, 'total': total, 'draw': draw}

    def process(self, pre_search_condition=None, **kwargs):
        """
        function to be called outside to get the footer search condition,
        apply the search in DB and render the serialized result.

        :param pre_search_condition: None/OrderedDict: pre search condition to
          be applied before applying the one getting from footer
        :param kwargs: dict: search parameters got from footer
        :return: dict: contains the filtered data, total number of records,
            number of filtered records and drawing number.
        """
        records = self.query_by_args(pre_search_condition=pre_search_condition,
                                     **kwargs)
        serializer = self.serializer(records['items'], many=True)
        result = {
            'data': serializer.data,
            'draw': records['draw'],
            'recordsTotal': records['total'],
            'recordsFiltered': records['count'],
        }
        return result
