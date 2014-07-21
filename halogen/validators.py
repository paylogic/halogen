"""Halogen basic type validators."""

from . import exceptions


class Validator(object):

    """Base validator."""

    @classmethod
    def validate(cls, value):
        """Validate the value.

        :param value: Value to validate.

        :raises: :class:`halogen.exception.ValidationError` exception when value is invalid.
        """


class Length(Validator):

    """Length validator that checks the length of a List-like type."""

    def __init__(self, min_length=None, max_length=None):
        """Length validator constructor.

        :param min_length: Minimum length, optional.
        :param max_length: Maximum length, optional.
        """
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        """Validate the length of a list.

        :param value: List of values.

        :raises: :class:`halogen.exception.ValidationError` exception when length of the list is less than
            minimum or greater than maximum.
        """
        length = len(value)
        if self.min_length is not None and length < self.min_length:
            raise exceptions.ValidationError("Length is less than {0}".format(self.min_length))

        if self.max_length is not None and length > self.max_length:
            raise exceptions.ValidationError("Length is greater than {0}".format(self.max_length))
