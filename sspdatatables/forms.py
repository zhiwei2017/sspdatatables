"""
Abstract form class to generating the choice fields dynamically
according to the value of 'fields' defined in Meta class
"""
from django.forms import forms


class AbstractFilterForm(forms.Form):
    """
    abstract django form, which can generate the ChoiceField dynamically.
    Aiming is to simplify the usage of the DataTables class and reducing
    the duplicate code (at least code with same structure).

    The only thing that the user to do is define the get choice function
    for all the choice fields, and the name of the get choice function
    should be in form of 'get_<field name>_choice>'. This class will
    automatically find the corresponding get choice function for each
    choice field.
    """
    def __new__(cls, *args, **kwargs):
        """
        used for checking the definition of the 'fields' variable in Meta
        class to make sure in the subclass it must be not None and its
        type is list of tuples.

        :param args: list: arguments in order
        :param kwargs:: dict : keyword arguments
        :return: an instance
        """
        assert (isinstance(cls.Meta.fields, list) and len(cls.Meta.fields) and
                all(isinstance(n, tuple) for n in cls.Meta.fields)), "'fields' must be a non-empty list of tuples."
        return super(AbstractFilterForm, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        """
        dynamically defining the ChoiceFields according to the value of 'fields'
        in Meta class

        :param args: list: arguments in order
        :param kwargs:: dict : keyword arguments
        """
        super(AbstractFilterForm, self).__init__(*args, **kwargs)
        for field_name, field_type in self.Meta.fields:
            self.fields[field_name] = field_type(required=False, choices=getattr(self, 'get_'+field_name+'_choices'))

    class Meta:
        """
        :param fields: list of tuples: the form should be:
            [("<field_name>", <forms.ChoiceField or forms.MultiChoiceField>), ]
        """
        fields = None
