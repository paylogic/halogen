"""Test the serialization of a complex type."""

from decimal import Decimal

import halogen
import json


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


def test_creation_counter():
    """Test that JSON fields are in the order which they were defined in Python"""
    class OrderedSchema1(halogen.Schema):
        self = halogen.Link('http://somewhere.com')
        foo = halogen.Attr('bar')
        hello = halogen.Attr()
        person = halogen.Embedded(PersonSchema)

    data = {
        "hello": "world",
        "person": Person("John", "Smith"),
    }
    serialized = OrderedSchema1.serialize(data)
    rv = json.dumps(serialized)
    assert rv == ('{"_links": {"self": {"href": "http://somewhere.com"}}, "foo": "bar", "hello": '
                  '"world", "_embedded": {"person": {"name": "John", "surname": "Smith"}}}')

    class OrderedSchema2(halogen.Schema):
        self = halogen.Link('http://somewhere.com')
        hello = halogen.Attr()
        foo = halogen.Attr('bar')
        person = halogen.Embedded(PersonSchema)

    serialized = OrderedSchema2.serialize(data)
    rv = json.dumps(serialized)
    assert rv == ('{"_links": {"self": {"href": "http://somewhere.com"}}, "hello": "world", '
                  '"foo": "bar", "_embedded": {"person": {"name": "John", "surname": "Smith"}}}')
