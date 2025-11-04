"""Test the serialization of a complex type."""

import json

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


class Event(object):
    """A event has a name."""

    def __init__(self, name):
        """Create a new Event."""
        self.name = name


class AmountType(halogen.types.Type):
    """A type that matches the Amount class."""

    @classmethod
    def serialize(cls, value):
        """Serialize the amount."""
        return dict(currency=value.currency, amount=str(value.amount))


em = halogen.Curie(name="em", href="https://docs.event-manager.com/{rel}.html", templated=True, type="text/html")


class PersonSchema(halogen.Schema):
    """A schema that matches the Person class."""

    @halogen.Link()
    def self(self):
        return "/foobar/1"

    name = halogen.Attr()
    surname = halogen.Attr()


class EventSchema(halogen.Schema):
    """A schema that matches the Event class."""

    @halogen.Link()
    def self(self):
        return "/foobar/1"

    name = halogen.Attr()


class NestedSchema(halogen.Schema):
    """A combination of a Person, an attribute is_friend, and a price."""

    self = halogen.Link("/events/activity-event{?uid}", type="application/pdf", templated=True)
    person = halogen.Attr(PersonSchema)
    is_friend = halogen.Attr()
    price = halogen.Attr(AmountType)
    events = halogen.Embedded(halogen.types.List(EventSchema), attr=lambda collection: collection["events"], curie=em)


def test_nested():
    """Test if serialization of nested data works correctly."""
    nested_data = {
        "person": Person("John", "Smith"),
        "is_friend": True,
        "price": Amount("EUR", Decimal("13.37")),
        "events": [Event("Name")],
    }
    serialized = NestedSchema.serialize(nested_data)
    assert dict(serialized) == {
        "_links": {
            "self": {"href": "/events/activity-event{?uid}", "templated": True, "type": "application/pdf"},
            "curies": [
                {
                    "href": "https://docs.event-manager.com/{rel}.html",
                    "name": "em",
                    "templated": True,
                    "type": "text/html",
                }
            ],
        },
        "person": {"_links": {"self": {"href": "/foobar/1"}}, "name": "John", "surname": "Smith"},
        "is_friend": True,
        "price": {"currency": "EUR", "amount": "13.37"},
        "_embedded": {"em:events": [{"_links": {"self": {"href": "/foobar/1"}}, "name": "Name"}]},
    }


def test_creation_counter():
    """Test that JSON fields are in the order which they were defined in Python."""

    class OrderedSchema1(halogen.Schema):
        self = halogen.Link("http://somewhere.com")
        foo = halogen.Attr("bar")
        hello = halogen.Attr()
        person = halogen.Embedded(PersonSchema)

    data = {
        "hello": "world",
        "person": Person("John", "Smith"),
    }
    serialized = OrderedSchema1.serialize(data)
    rv = json.dumps(serialized)
    assert rv == (
        '{"_links": {"self": {"href": "http://somewhere.com"}}, "foo": "bar", "hello": "world", "_embedded": '
        '{"person": {"_links": {"self": {"href": "/foobar/1"}}, "name": "John", "surname": "Smith"}}}'
    )

    class OrderedSchema2(halogen.Schema):
        self = halogen.Link("http://somewhere.com")
        hello = halogen.Attr()
        foo = halogen.Attr("bar")
        person = halogen.Embedded(PersonSchema)

    serialized = OrderedSchema2.serialize(data)
    rv = json.dumps(serialized)
    assert rv == (
        '{"_links": {"self": {"href": "http://somewhere.com"}}, "hello": "world", "foo": "bar", "_embedded": {'
        '"person": {"_links": {"self": {"href": "/foobar/1"}}, "name": "John", "surname": "Smith"}}}'
    )


def test_empty_compartment_does_not_appear():
    """Test that an empty compartment does not appear in a serialized document."""

    class Schema(halogen.Schema):
        user1 = halogen.Embedded(PersonSchema, required=False)
        user2 = halogen.Embedded(PersonSchema)

    serialized = Schema.serialize({"user2": Person("John", "Smith")})
    rv = json.dumps(serialized)
    assert rv == (
        '{"_embedded": {"user2": {"_links": {"self": {"href": "/foobar/1"}}, "name": "John", "surname": ' '"Smith"}}}'
    )
