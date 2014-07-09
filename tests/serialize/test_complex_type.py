"""Test the serialization of a complex type."""

from decimal import Decimal

import halogen


class Amount(object):

    """A combination of currency and amount."""

    def __init__(self, currency, amount):
        """Create a new Amount."""
        self.currency = currency
        self.amount = amount


class Person(object):

    """A person has a name and surname."""

    def __init__(self, name, surname):
        """Create a new Person."""
        self.name = name
        self.surname = surname


class AmountType(halogen.types.Type):

    """A type that matches the Amount class."""

    @classmethod
    def serialize(cls, value):
        """Serialize the amount."""
        return dict(
            currency=value.currency,
            amount=str(value.amount)
        )


class PersonSchema(halogen.Schema):

    """A schema that matches the Person class."""

    name = halogen.Attr()
    surname = halogen.Attr()


class NestedSchema(halogen.Schema):

    """A combination of a Person, an attribute is_friend, and a price."""

    person = halogen.Attr(PersonSchema)
    is_friend = halogen.Attr()
    price = halogen.Attr(AmountType)


def test_nested():
    """Test if serialization of nested data works correctly."""
    nested_data = {
        "person": Person("John", "Smith"),
        "is_friend": True,
        "price": Amount("EUR", Decimal("13.37")),
    }
    serialized = NestedSchema.serialize(nested_data)
    assert serialized == {
        "person": {
            "surname": "Smith",
            "name": "John"
        },
        "price": {
            "currency": "EUR",
            "amount": "13.37"
        },
        "is_friend": True
    }
