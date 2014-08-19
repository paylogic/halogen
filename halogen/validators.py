"""Halogen basic type validators."""

from halogen import exceptions


class Validator(object):

    """Base validator."""

    @classmethod
    def validate(cls, value):
        """Validate the value.

        :param value: Value to validate.

        :raises: :class:`halogen.exception.ValidationError` exception when value is invalid.
        """


class LessThanEqual(Validator):

    value_err = "{0} is bigger than {1}"

    def __init__(self, value, value_err=None):

        self.value = value() if callable(value) else value

        if value_err is not None:
            self.value_err = value_err

    def validate(self, value):

        if value > self.value:
            raise exceptions.ValidationError(self.value_err.format(value, self.value))

        return True


class GreatThanEqual(Validator):

    value_err = "{0} is smaller than {1}"

    def __init__(self, value, value_err=None):

        self.value = value() if callable(value) else value

        if value_err is not None:
            self.value_err = value_err

    def validate(self, value):

        if value < self.value:
            raise exceptions.ValidationError(self.value_err.format(value, self.value))

        return True


class Length(Validator):

    """Length validator that checks the length of a List-like type."""

    min_err = "Length is less than {0}"
    max_err = "Length is greater than {0}"

    def __init__(self, min_length=None, max_length=None, min_err=None, max_err=None):
        """Length validator constructor.

        :param min_length: Minimum length, optional.
        :param max_length: Maximum length, optional.
        """
        self.min_length = min_length
        self.max_length = max_length

        if min_err is not None:
            self.min_err = min_err

        if max_err is not None:
            self.max_err = max_err

    def validate(self, value):
        """Validate the length of a list.

        :param value: List of values.

        :raises: :class:`halogen.exception.ValidationError` exception when length of the list is less than
            minimum or greater than maximum.
        """
        try:
            length = len(value)
        except TypeError:
            length = 0

        if self.min_length is not None and length < self.min_length:
            raise exceptions.ValidationError(self.min_err.format(self.min_length))

        if self.max_length is not None and length > self.max_length:
            raise exceptions.ValidationError(self.max_err.format(self.max_length))


class Range(object):

    """Validator which succeeds if the value it is passed is greater or equal to ``min`` and less than or equal to
    ``max``.  If ``min`` is not specified, or is specified as ``None``, no lower bound exists.  If ``max`` is not
    specified, or is specified as ``None``, no upper bound exists.
    """

    min_err = '{val} is less than minimum value {min}'
    max_err = '{val} is greater than maximum value {max}'

    def __init__(self, min=None, max=None, min_err=None, max_err=None):
        """Range validator constructor.
        :param min: Minimal value of range, optional.
        :param max: Maximal value of range, optional.
        :param min_err: ValidationError message if value is less than minimal value of range.
        :param max_err: ValidationError message if value is greater than maximal value of range.
        """
        self.min = min
        self.max = max
        if min_err is not None:
            self.min_err = min_err
        if max_err is not None:
            self.max_err = max_err

    def validate(self, value):
        """Validate value.

        :param value: Value which should be validated.

        :raises: :class:`halogen.exception.ValidationError` exception when either if value less than min in case when
        min is not None or if value greater than max in case when max is not None.
        """
        if self.min is not None:
            if value < (self.min() if callable(self.min) else self.min):
                raise exceptions.ValidationError(self.min_err.format(val=value, min=self.min))

        if self.max is not None:
            if value > (self.max() if callable(self.max) else self.max):
                raise exceptions.ValidationError(self.max_err.format(val=value, max=self.max))
