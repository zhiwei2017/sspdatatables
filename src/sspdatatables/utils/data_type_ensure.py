"""
Module to hold the functionality for ensuring the given value is in the given
data type.
"""


def ensure(data_type, check_value, default_value=None):
    """
    function to ensure the given check value is in the given data type, if yes,
    return the check value directly, otherwise return the default value

    :param data_type: different data type: can be int, str, list, tuple etc,
      must be python supportable data type or new defined data type
    :param check_value: different value: the value to check
    :param default_value: None/ different value: provide the default value
    :return: check value or default value
    """
    if default_value is not None and not isinstance(default_value, data_type):
        raise ValueError("default_value must be the value in the given data "
                         "type.")
    elif isinstance(check_value, data_type):
        return check_value
    try:
        new_value = data_type(check_value)
    except:
        return default_value
    return new_value
