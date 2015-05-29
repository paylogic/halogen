"""Class/functions for validation."""

import uuid
try:
    from http import client as httplib
except ImportError:  # pragma: no cover
    import httplib

from flask import abort
from werkzeug.routing import BaseConverter


class UidValidator(BaseConverter):

    """Validates the `UID` bit of the route."""

    def to_python(self, value):
        """Check if the value is a valid `UID`.

        :param value: The `UID` value.

        :raises: Abort the request.

        :return: Value as it is.
        """
        try:
            uuid.UUID(value)
        except ValueError:
            abort(httplib.BAD_REQUEST, u'Invalid UID {0}'.format(value))

        return value
