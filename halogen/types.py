"""Halogen basic types."""


class Type(object):

    """Base class for creating types."""

    @classmethod
    def serialize(cls, value):
        """Serialization of value."""
        return value

    @classmethod
    def deserialize(cls, value):
        """Deserialization of value."""
        return value

    @staticmethod
    def is_type(value):
        """Is value an instance or subclass of the class Type."""
        if isinstance(value, type):
            return issubclass(value, Type)
        return isinstance(value, Type)


class List(Type):

    """List type for Halogen schema attribute."""

    def __init__(self, item_type=None, allow_scalar=False):
        """Create a new List.

        :param item_type: Item type or schema.
        :param allow_scalar: Automatically convert scalar value to the list.
        """
        super(List, self).__init__()
        self.item_type = item_type or Type
        self.allow_scalar = allow_scalar

    def serialize(self, value, **kwargs):
        """Serialize every item of the list."""
        return [self.item_type.serialize(val, **kwargs) for val in value]

    def deserialize(self, value, **kwargs):
        """Deserialize every item of the list."""
        if self.allow_scalar and not isinstance(value, (list, tuple)):
            value = [value]
        return [self.item_type.deserialize(val, **kwargs) for val in value]
