from decimal import Decimal

import halogen


class Amount(object):
    def __init__(self, currency, amount):
        self.currency = currency
        self.amount = amount


class Person(object):
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname


class AmountType(halogen.types.Type):
    @classmethod
    def serialize(cls, value):
        return dict(
            currency=value.currency,
            amount=str(value.amount)
        )


class PersonSchema(halogen.Schema):
    name = halogen.Attr()
    surname = halogen.Attr()


class NestedSchema(halogen.Schema):
    person = halogen.Attr(PersonSchema)
    is_friend = halogen.Attr()
    price = halogen.Attr(AmountType)


def test_nested():
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
