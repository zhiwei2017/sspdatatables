"""
Module defines the decorator for checking the request passed to the Django views
function is ajax request and its request method is as expected
"""
from django.http import JsonResponse, HttpRequest


def ensure_ajax(valid_request_methods, error_response_context=None):
    """
    Intends to ensure the received the request is ajax request and it is
    included in the valid request methods

    :param valid_request_methods: list: list of valid request methods, such as
      'GET', 'POST'
    :param error_response_context: None/dict: context dictionary to render, if
      error occurs
    :return: function
    """
    def real_decorator(view_func):
        def wrap_func(request, *args, **kwargs):
            if not isinstance(request, HttpRequest):
                # make sure the request is a django httprequest
                return generate_error_json_response("Invalid request!",
                                                    error_response_context)
            elif not request.is_ajax():
                # ensure the request is an ajax request
                return generate_error_json_response("Invalid request type!",
                                                    error_response_context)
            elif request.method not in valid_request_methods:
                # check if the request method is in allowed request methods
                return generate_error_json_response("Invalid request method!",
                                                    error_response_context)
            else:
                return view_func(request, *args, **kwargs)
        wrap_func.__doc__ = view_func.__doc__
        wrap_func.__name__ = view_func.__name__
        return wrap_func
    return real_decorator


def generate_error_json_response(error_dict, error_response_context=None):
    """
    Intends to build an error json response. If the error_response_context is
    None, then we generate this response using data tables format

    :param error_dict: str/dict: contains the error message(s)
    :param error_response_context: None/dict: context dictionary to render, if
      error occurs
    :return: JsonResponse
    """
    response = error_dict
    if isinstance(error_dict, str):
        response = {"error": response}
    if error_response_context is None:
        error_response_context = {
            'draw': 0, 'recordsTotal': 0, 'recordsFiltered': 0, 'data': []
        }
    response.update(error_response_context)
    return JsonResponse(response)
