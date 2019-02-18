"""vnd.error support."""

from __future__ import unicode_literals

import halogen
import six


class Error(Exception):
    """Base exception."""

    def __init__(self, message, path=None, errors=None):
        """Create an error.

        :param message: Error message.
        :param path: Optional JSON Pointer path.
        :param errors: Optional nested errors.
        """
        self.message = message
        if path is not None:
            self.path = path
        if errors is not None:
            self.errors = errors

    @classmethod
    def from_validation_exception(cls, exception, **kwargs):
        """Create an error from validation exception."""
        errors = []

        def flatten(error, path=""):
            if isinstance(error, halogen.exceptions.ValidationError):
                if not path.endswith("/"):
                    path += "/"
                if error.attr is not None:
                    path += error.attr
                elif error.index is not None:
                    path += six.text_type(error.index)

                for e in error.errors:
                    flatten(e, path)
            else:
                message = error
                if isinstance(error, Exception):
                    try:
                        message = error.message
                    except AttributeError:
                        message = six.text_type(error)
                # TODO: i18n
                errors.append(Error(message=message, path=path))

        flatten(exception)
        message = kwargs.pop("message", "Validation error.")
        return cls(message=message, errors=sorted(errors, key=lambda error: error.path or ""), **kwargs)


class VNDError(halogen.Schema):
    """Error response schema for application/vnd.error+json type."""

    class List(halogen.types.List):
        """List of errors."""

        @property
        def item_type(self):
            return VNDError

        @item_type.setter
        def item_type(self, value):
            """Ignored."""

    message = halogen.Attr(required=True)
    logref = halogen.Attr(required=False)
    path = halogen.Attr(required=False)

    errors = halogen.Embedded(List(), required=False)
