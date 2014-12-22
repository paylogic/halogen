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
    class OrderedSchema(halogen.Schema):
        self = halogen.Link('http://somewhere.com')
        foo = halogen.Attr('bar')
        hello = halogen.Attr()
        person = halogen.Embedded(PersonSchema)

    data = {
        "hello": "world",
        "person": Person("John", "Smith"),
    }
    serialized = OrderedSchema.serialize(data)
    rv = json.dumps(serialized)
    assert rv == ('{"_links": {"self": {"href": "http://somewhere.com"}}, "foo": "bar", "hello": '
                  '"world", "_embedded": {"person": {"name": "John", "surname": "Smith"}}}')


def test_embedded_attr_with_no_value():
    """Test that the _embedded compartment does not exist in a serialized document if none of the
    embedded resource are required."""

    class UnrequiredEmbeddedSchema(halogen.Schema):
        self = halogen.Link('http://somewhere.com')
        foo = halogen.Attr('bar')
        person = halogen.Embedded(PersonSchema, required=False)

    data = {
        "hello": "world",
        "person": None,
    }
    serialized = UnrequiredEmbeddedSchema.serialize(data)
    rv = json.dumps(serialized)
    assert rv == ('{"_links": {"self": {"href": "http://somewhere.com"}}, "foo": "bar"}')


def test_link_with_no_value_when_not_required_does_not_render():
    """Test that when a link accessor returns None and the link is not required, that it does
    not render in the serialized document"""
    class UnrequiredLinksSchema(halogen.Schema):
        self = halogen.Link(attr=None, required=False)
        somewhere = halogen.Link(attr=lambda _: None, required=False)
        foo = halogen.Attr('bar')

    serialized = UnrequiredLinksSchema.serialize({})
    rv = json.dumps(serialized)
    assert rv == ('{"foo": "bar"}')


def test_embedded_list_with_embedded_attr_with_no_value():
    class UnrequiredEmbeddedSchema(halogen.Schema):
        self = halogen.Link('http://somewhere.com')
        foo = halogen.Attr('bar')
        person = halogen.Embedded(PersonSchema, required=False)

    class UnrequiredEmbeddedSchemaCollection(halogen.Schema):
        items = halogen.Embedded(attr_type=halogen.types.List(UnrequiredEmbeddedSchema))

    data = {
        'items': [{
            "hello": "world",
            "person": None,
        }]
    }

    serialized = UnrequiredEmbeddedSchemaCollection.serialize(data)
    rv = json.dumps(serialized)
    assert rv == ('{"_embedded": {"items": [{"_links": {"self": {"href": "http://somewhere.com"}}, "foo": "bar"}]}}')
