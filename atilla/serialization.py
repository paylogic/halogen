"""API serialization."""

import functools
from atilla import response


def serialize(schema_class):
    """Serialize the API call result with the schema.

    :param schema_class: Schema class to use for the serialization.

    :return: Decorator that applies the serialization to a function.
    """
    def wrapper(func):

        func.schema = schema_class

        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            resp = func(*args, **kwargs)
            params = {}
            context = {}
            if type(resp) == tuple:
                data, context = resp[:2]
                if len(resp) == 3:
                    params = resp[2]
            else:
                data = resp
            return response.api_response(schema_class.serialize(data, **context), **params)
        return func_wrapper

    return wrapper
