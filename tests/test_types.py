"""Test halogen types."""
import decimal
import datetime
import enum
from typing import Union

import pytz
import six

import mock
import pytest

from pytz import timezone
from halogen import types
from halogen.exceptions import ValidationError


def test_type():
    """Test very basic."""
    type_ = types.Type()
    value = object()
    assert value is type_.serialize(value)
    assert value is type_.deserialize(value)


def test_list():
    """Test list."""
    type_ = types.List()
    value = [object(), object()]
    assert value == type_.serialize(value)
    assert value == type_.deserialize(value)


@pytest.mark.parametrize("input", [{"foo": "bar"}, 42, 11.5, True, False, None, "", "foo"])
def test_list_bad_input(input):
    """Test that the deserialization fails correctly when the input is not a list, and scalars are not allowed"""
    type_ = types.List(allow_scalar=False)
    with pytest.raises(ValidationError, match=".*is not a list"):
        type_.deserialize(input)


@pytest.mark.parametrize(
    ["value", "serialized"],
    [
        (timezone("Europe/Amsterdam").localize(datetime.datetime(2018, 12, 23, 16, 20)), "2018-12-23T16:20:00+01:00"),
        (timezone("Europe/Amsterdam").localize(datetime.datetime(2018, 5, 14, 16, 20)), "2018-05-14T16:20:00+02:00"),
        (timezone("UTC").localize(datetime.datetime(2018, 5, 14, 16, 20)), "2018-05-14T16:20:00+00:00"),
    ],
)
def test_isodatetime(value, serialized):
    """Test iso datetime."""
    type_ = types.ISODateTime()
    assert type_.serialize(value) == serialized
    assert type_.deserialize(serialized) == value.replace(microsecond=0)


def test_isoutcdatetime():
    """Test iso datetime."""
    type_ = types.ISOUTCDateTime()
    value = datetime.datetime.now(pytz.timezone("CET")).astimezone(pytz.UTC)
    serialized = value.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert type_.serialize(value) == serialized
    assert type_.deserialize(serialized) == value.replace(microsecond=0)


def test_isoutcdatetime_bc():
    """Test iso datetime with year before 1900."""
    type_ = types.ISOUTCDateTime()
    value = datetime.datetime(1800, 1, 1, tzinfo=pytz.timezone("CET"))
    assert type_.serialize(value) == "1799-12-31T23:00:00Z"
    assert type_.deserialize("1799-12-31T23:00:00Z") == value.replace(microsecond=0)


@pytest.mark.parametrize("value", ["01.01.1981 11:11:11", "123x3"])
def test_isoutcdatetime_wrong(value):
    """Test iso datetime when wrong value is passed."""
    type_ = types.ISOUTCDateTime()
    with pytest.raises(ValueError) as err:
        type_.deserialize(value)
    assert err.value.args[0] == "'{0}' is not a valid ISO-8601 datetime".format(value)


def test_isodate():
    """Test iso datetime."""
    type_ = types.ISOUTCDate()
    value = datetime.datetime.now(pytz.timezone("CET")).date()
    serialized = value.strftime("%Y-%m-%d")
    assert type_.serialize(value) == serialized
    assert type_.deserialize(serialized) == value


def test_string():
    """Test string type."""
    type_ = types.String()
    value = object()
    assert type_.serialize(value) == six.text_type(value)
    assert type_.serialize(None) == ""
    assert type_.deserialize("") == ""
    assert type_.deserialize("Some") == "Some"
    assert type_.deserialize({"key": "value"}) == "{'key': 'value'}"


def test_int():
    """Test int type."""
    type_ = types.Int()
    value = 123
    assert type_.serialize(value) == value
    assert type_.deserialize(str(value)) == value
    with pytest.raises(ValueError) as err:
        type_.deserialize("not-int")
    assert err.value.args[0] == "'not-int' is not an integer"


@pytest.mark.parametrize(
    ["value", "clean_value", "expected"],
    [
        (True, True, True),
        (1, 1, True),
        (0, 0, False),
        ("1", 1, True),
        ("0", 0, False),
        ("true", "1", True),
        ("True", "0", True),
        ("false", 0, False),
        ("False", 0, False),
        (None, None, None),
    ],
)
def test_boolean(value, clean_value, expected):
    """Test boolean type."""
    type_ = types.Boolean()
    assert type_.serialize(clean_value) is expected
    assert type_.deserialize(value) is expected


def test_boolean_invalid():
    """Test boolean type when value provided is not valid."""
    type_ = types.Boolean()
    with pytest.raises(ValueError):
        type_.deserialize("not-int")


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        ({}, "Amount object has to have currency and amount fields."),
        (1, "Value cannot be parsed to Amount."),
        ("INV1", "'INV' is not a valid currency."),
        ("EURnot-number", "'not-number' cannot be parsed to decimal."),
        ("EUR 11.234", "'11.234' has more than 2 decimal places."),
    ],
)
def test_amount_invalid(value, expected):
    """Test amount type deserialization when invalid value is passed."""
    type_ = types.Amount(currencies=["EUR"], amount_class=dict)
    with pytest.raises(ValueError) as err:
        type_.deserialize(value)
    assert err.value.args[0] == expected


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        ("EUR1.22", {"currency": "EUR", "amount": decimal.Decimal("1.22")}),
        (None, None),
        ({"amount": "12.34", "currency": "EUR"}, {"currency": "EUR", "amount": decimal.Decimal("12.34")}),
        ("EUR12.34", {"currency": "EUR", "amount": decimal.Decimal("12.34")}),
    ],
)
def test_amount_valid(value, expected):
    """Test amount type with valid input."""
    type_ = types.Amount(currencies=["EUR"], amount_class=dict)
    assert type_.deserialize(value) == expected


def test_amount_serialize():
    """Test amount serialize."""
    type_ = types.Amount(currencies=["EUR"], amount_class=dict)
    amount = mock.Mock()
    amount.as_quantized().as_tuple.return_value = (1, 2)
    with pytest.raises(ValueError) as err:
        type_.serialize(amount)
    assert err.value.args[0] == "'1' is not a valid currency."

    amount.as_quantized().as_tuple.return_value = ("EUR", 11.23)
    assert type_.serialize(amount) == {"amount": "11.23", "currency": "EUR"}
    assert type_.serialize(None) is None


def test_nullable_type():

    nested_type = mock.MagicMock(
        serialize=mock.MagicMock(return_value="serialize"),
        deserialize=mock.MagicMock(return_value="deserialize"),
    )

    nullable = types.Nullable(nested_type)

    assert nullable.serialize("test") == "serialize"
    assert nullable.serialize(None) is None

    assert nullable.deserialize("test") == "deserialize"
    assert nullable.deserialize(None) is None


@pytest.mark.parametrize(
    ["value", "use_values"],
    [
        (1, True),
        ("FOO", False),
        ("BAR", False),
    ],
)
def test_enum(value: Union[int, str, None], use_values: bool):
    class TestEnum(enum.Enum):
        FOO = 1
        BAR = 2

    type_ = types.Enum(TestEnum, use_values=use_values)

    assert isinstance(type_.deserialize(value), TestEnum)


@pytest.mark.parametrize(
    ["value", "use_values", "expected_error"],
    [
        (1, False, "Unknown value."),
        (3, True, "Unknown value."),
        ("FOO", True, "Unknown value."),
        ("BAR", True, "Unknown value."),
        ("NONEXISTENT", False, "Unknown value."),
        (1.5, True, "Unknown value.")
    ],
)
def test_invalid_enum(value: Union[int, str, float], use_values: bool, expected_error: str):
    class TestEnum(enum.Enum):
        FOO = 1
        BAR = 2

    type_ = types.Enum(TestEnum, use_values=use_values)

    with pytest.raises(ValueError) as err:
        type_.deserialize(value)

    assert expected_error == str(err.value)


def test_nullable_enum():
    class TestEnum(enum.Enum):
        FOO = 1
        BAR = 2

    type_ = types.Enum(TestEnum, use_values=False)

    assert type_.deserialize(None) is None
