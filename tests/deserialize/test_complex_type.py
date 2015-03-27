"""Test functionality of Halogen when using a complex type."""

import copy
from decimal import Decimal, InvalidOperation

import pytest

import halogen
import halogen.types
from halogen import exceptions


class Amount(halogen.types.Type):

    """A combination of currency and amount."""

    @classmethod
    def deserialize(cls, value):
        """Serialize an amount."""
        try:
            amount = Decimal(value["amount"])
        except InvalidOperation:
            raise exceptions.ValidationError('Invalid decimal for amount.')
        return dict(
            amount=amount,
            currency=value["currency"],
        )


class Person(halogen.Schema):

    """A person has a name and surname."""

    name = halogen.Attr()
    surname = halogen.Attr()


class Product(halogen.Schema):

    """A product has a name and quantity."""

    name = halogen.Attr()
    quantity = halogen.Attr()


class NestedSchema(halogen.Schema):

    """An example nested schema, with a person, an is_friend attribute, and a price."""

    person = halogen.Attr(Person)
    is_friend = halogen.Attr()
    price = halogen.Attr(Amount)
    products = halogen.Attr(
        halogen.types.List(
            Product,
            allow_scalar=True,
            validators=[
                halogen.validators.Length(
                    min_length=0,
                ),
            ],
        ),
        default=[],
    )


def test_nested():
    """Test deserialization of a nested type."""
    nested_data = {
        "person": {
            "name": "Johann",
            "surname": "Gambolputty"
        },
        "is_friend": True,
        "price": {"currency": "EUR", "amount": "13.37"},
        "products": []
    }

    expected = copy.deepcopy(nested_data)
    expected["price"]["amount"] = Decimal(expected["price"]["amount"])
    deserialized = NestedSchema.deserialize(nested_data)
    assert deserialized == expected


@pytest.mark.parametrize(["data", "errors"], [
    (
        {
            "is_friend": True,
            "price": {"currency": "EUR", "amount": "wrong_amount"}
        }, {
            "attr": "<root>",
            "errors": [
                {
                    "errors": [
                        {
                            "type": "str",
                            "error": "Missing attribute."
                        }
                    ],
                    "attr": "person"
                },
                {
                    "attr": "price",
                    "errors": [
                        {
                            "type": "str",
                            "error": "Invalid decimal for amount."
                        }
                    ],
                }
            ]
        }
    ),
    (
        {
            "person": "",
            "is_friend": True,
            "price": {"currency": "EUR", "amount": "wrong_amount"}
        }, {
            "attr": "<root>",
            "errors": [
                {
                    "errors": [
                        {
                            "errors": [
                                {
                                    "type": "str",
                                    "error": "Missing attribute."
                                }
                            ],
                            "attr": "name"
                        },
                        {
                            "errors": [
                                {
                                    "type": "str",
                                    "error": "Missing attribute."
                                }
                            ],
                            "attr": "surname"
                        }
                    ],
                    "attr": "person"
                },
                {
                    "attr": "price",
                    "errors": [
                        {
                            "type": "str",
                            "error": "Invalid decimal for amount."
                        }
                    ],
                }
            ]
        }
    ),
    (
        {
            "person": {
                "name": "Some name"
            },
            "is_friend": True,
            "price": {"currency": "EUR", "amount": "wrong_amount"}
        }, {
            "attr": "<root>",
            "errors": [
                {
                    "errors": [
                        {
                            "errors": [
                                {
                                    "type": "str",
                                    "error": "Missing attribute."
                                }
                            ],
                            "attr": "surname"
                        }
                    ],
                    "attr": "person"
                },
                {
                    "attr": "price",
                    "errors": [
                        {
                            "type": "str",
                            "error": "Invalid decimal for amount."
                        }
                    ],
                }
            ]
        }
    ),
    (
        {
            "person": {
                "name": "Some name",
                "surname": "Some surname"
            },
            "is_friend": True,
            "price": {"currency": "EUR", "amount": "12.23"},
            "products": [
                {
                    "name": "Some name",
                    "quantity": 1
                },
                {
                    "name": "Some name",
                },
            ]
        }, {
            "errors": [
                {
                    "errors": [
                        {
                            "index": 1,
                            "errors": [
                                {
                                    "errors": [
                                        {
                                            "type": "str",
                                            "error": "Missing attribute."
                                        }
                                    ],
                                    "attr": "quantity"
                                }
                            ]
                        }
                    ],
                    "attr": "products"
                }
            ],
            "attr": "<root>"
        }
    ),
])
def test_missing_attribute(data, errors):
    """Test if an exception is raised when an attribute is missing."""
    with pytest.raises(halogen.exceptions.ValidationError) as err:
        NestedSchema.deserialize(data)
    assert err.value.to_dict() == errors
