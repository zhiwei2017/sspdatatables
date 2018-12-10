"""
Module contains the helper function for the template
"""
from django import template

register = template.Library()


@register.filter
def get_form_bound_field(form, field_name):
    """
    Intends to get the bound field from the form regarding the field name

    :param form: Django Form: django form instance
    :param field_name: str: name of the field in form instance
    :return: Django Form bound field
    """
    field = form.fields[field_name]
    field = field.get_bound_field(form, field_name)
    return field
