"""Halogen basic types."""


class Type(object):
    """Base class for creating types."""

    @classmethod
    def serialize(cls, value):
        """Serialization of value."""
        return value

    @classmethod
    def deserialize(cls, value):
        """Desirialization of value."""
        return value

    @classmethod
    def is_type(cls, value):
        """Is value instance or subclass of this class."""
        if isinstance(value, type):
            return issubclass(value, cls)
        return isinstance(value, cls)


class List(Type):
    """List type for Halogen schema attribute."""

    def __init__(self, item_type=None):
        super(List, self).__init__()
        self.item_type = item_type or Type

    def serialize(self, value):
        """Overrided serialize for returning list of value's items."""
        return [self.item_type.serialize(val) for val in value]
