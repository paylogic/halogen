import copy
from decimal import Decimal, InvalidOperation

import pytest

import halogen
import halogen.types
from halogen import exceptions


class Amount(halogen.types.Type):
    @classmethod
    def deserialize(cls, value):
        try:
            return dict(
                currency=value["currency"],
                amount=Decimal(value["amount"])
            )
        except InvalidOperation as e:
            raise exceptions.ValidationError(e)


class Person(halogen.Schema):
    name = halogen.Attr()
    surname = halogen.Attr()


class NestedSchema(halogen.Schema):
    person = halogen.Attr(Person)
    is_friend = halogen.Attr()
    price = halogen.Attr(Amount)


def test_nested():
    """Test deserialization of a nested type."""

    nested_data = {
        "person": {
            "name": "Johann",
            "surname": "Gambolputty"
        },
        "is_friend": True,
        "price": {"currency": "EUR", "amount": "13.37"}
    }

    expected = copy.deepcopy(nested_data)
    expected["price"]["amount"] = Decimal(expected["price"]["amount"])
    deserialized = NestedSchema.deserialize(nested_data)
    assert deserialized == expected


def test_invalid_value():
    """Test errors reported for a broken nested type."""
    data = {
        "person": {
            "name": "hello",
            "surname": "bye"
        },
        "is_friend": True,
        "price": {"currency": "EUR", "amount": "wrong_amount"}
    }

    errors = {
        "attr": "<root>",
        "errors": [{
            "attr": "price",
            "errors": [{"type": "InvalidOperation", "error": "Invalid literal for Decimal: 'wrong_amount'"}],
        }]
    }

    with pytest.raises(halogen.exceptions.ValidationError) as e:
        NestedSchema.deserialize(data)
    errors = e.value.to_dict()
    assert errors["attr"] == "<root>"
    assert errors["errors"][0]["attr"] == "price"


def test_missing_attribute():
    data = {
        "is_friend": True,
        "price": {"currency": "EUR", "amount": "wrong_amount"}
    }
    # TODO improve
    with pytest.raises(halogen.exceptions.ValidationError):
        NestedSchema.deserialize(data)
