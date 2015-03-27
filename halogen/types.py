"""Halogen basic types."""
from .exceptions import ValidationError


class Type(object):

    """Base class for creating types."""

    def __init__(self, validators=None, *args, **kwargs):
        """Type constructor.

        :param validators: A list of :class:`halogen.validators.Validator` objects that check the validity of the
            deserialized value. Validators raise :class:`halogen.exception.ValidationError` exceptions when
            value is not valid.
        """
        self.validators = validators or []

    def serialize(self, value):
        """Serialization of value."""
        return value

    def deserialize(self, value):
        """Deserialization of value.

        :return: Deserialized value.
        :raises: :class:`halogen.exception.ValidationError` exception is value is not valid.
        """
        for validator in self.validators:
            validator.validate(value)

        return value

    @staticmethod
    def is_type(value):
        """Determine if value is an instance or subclass of the class Type."""
        if isinstance(value, type):
            return issubclass(value, Type)
        return isinstance(value, Type)


class List(Type):

    """List type for Halogen schema attribute."""

    def __init__(self, item_type=None, allow_scalar=False, *args, **kwargs):
        """Create a new List.

        :param item_type: Item type or schema.
        :param allow_scalar: Automatically convert scalar value to the list.
        """
        super(List, self).__init__(*args, **kwargs)
        self.item_type = item_type or Type()
        self.allow_scalar = allow_scalar

    def serialize(self, value, **kwargs):
        """Serialize every item of the list."""
        return [self.item_type.serialize(val, **kwargs) for val in value]

    def deserialize(self, value, **kwargs):
        """Deserialize every item of the list."""
        if self.allow_scalar and not isinstance(value, (list, tuple)):
            value = [value]
        value = super(List, self).deserialize(value)
        result = []
        errors = []

        for index, val in enumerate(value):
            try:
                item = self.item_type.deserialize(val, **kwargs)
            except ValidationError as exc:
                exc.index = index
                errors.append(exc)
            result.append(item)
        if errors:
            raise ValidationError(errors)
        return result
