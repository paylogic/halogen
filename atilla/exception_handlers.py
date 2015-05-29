"""Utility functions to map Exceptions to HTTP responses."""

try:
    from http import client as httplib
except ImportError:  # pragma: no cover
    import httplib
import werkzeug.exceptions
from atilla.response import vnd_error_response


def exception_handler(exception):
    """Handle the exceptions and prepares the vnd.error response.

    :param exception: Exception raised in the request/response cycle.
    :return: vnd.error response with the error details.
    """
    if isinstance(exception, werkzeug.exceptions.HTTPException):
        status_code = exception.code or httplib.INTERNAL_SERVER_ERROR
    else:
        status_code = httplib.INTERNAL_SERVER_ERROR

    return vnd_error_response(exception, status_code=status_code)
