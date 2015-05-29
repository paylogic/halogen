"""Exceptions for APIs."""

import werkzeug.exceptions


class ApiException(Exception):

    """An exception raised due to user error.

    Exceptions derived from ApiException will be logged automatically if raised.
    User will receive appropriate error response according to the content type.
    """

    description = 'API error.'
    error_type = 'API_ERROR'
    data = None

    def __init__(self, message, description=None, status_code=None, **kwargs):
        """Constructor.

        :param message: the message returned to the user.
        :param description: the message sent to the log.
        """
        self.message = message
        if description is not None or not hasattr(self, 'description'):
            self.description = description

        if status_code is not None:
            self.code = status_code
        if kwargs:
            self.data = kwargs


class NotFound(ApiException, werkzeug.exceptions.NotFound):

    """Not found."""

    description = 'Not found.'
    error_type = 'NOT_FOUND'


class BadRequest(ApiException, werkzeug.exceptions.BadRequest):

    """Bad request."""

    description = 'Bad request.'
    error_type = 'BAD_REQUEST'


class Forbidden(ApiException, werkzeug.exceptions.Forbidden):

    """Forbidden."""

    description = 'Forbidden.'
    error_type = 'FORBIDDEN'


class Unauthorized(ApiException, werkzeug.exceptions.Unauthorized):

    """Unauthorized."""

    description = 'Unauthorized.'
    error_type = 'UNAUTHORIZED'
