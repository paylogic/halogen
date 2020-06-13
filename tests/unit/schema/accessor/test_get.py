"""Test the functionality of the Accessor schema."""

import mock
import pytest

from tests.fixtures.common import VALUES, Obj

from halogen.schema import Accessor


def basic_obj_get(obj):
    """Return the value of attribute "value" of "obj"."""
    return obj.value


def basic_dict_get(dic):
    """Return the value of the key "value" from the dict."""
    return dic["value"]


@pytest.mark.parametrize("basic_object_value", VALUES)
def test_get_object_callable(basic_object_value, basic_object):
    """Test return value of get with object.

    Test if Accessor.get() returns correct results for an object,
    when used with a callable getter.
    """
    acc = Accessor(getter=basic_obj_get)
    assert acc.get(basic_object) == basic_object_value


def test_get_object_callable_called(mocked_inspect_getargspec, basic_object):
    """Test if Accessor.get() calls Accessor.getter() if getter is callable."""
    acc = Accessor()
    acc.getter = mock.Mock()
    acc.get(basic_object)

    acc.getter.assert_called_once_with(basic_object)


@pytest.mark.parametrize("basic_object_value", VALUES)
def test_get_object_string(basic_object, basic_object_value):
    """Test if Accessor.get() returns correct results when used with a dotted string."""
    acc = Accessor(getter="value")
    assert acc.get(basic_object) == basic_object_value


@pytest.mark.parametrize("basic_dict_value", VALUES)
def test_get_dict_value(basic_dict_value, basic_dict):
    """Test return value of get with dict.

    Test if Accessor.get() returns correct results for an object,
    when used with a callable getter.
    """
    acc = Accessor(getter=basic_dict_get)
    assert acc.get(basic_dict) == basic_dict_value


@pytest.mark.parametrize("basic_dict_value", VALUES)
def test_get_dict_string(basic_dict_value, basic_dict):
    """Test return value of get with dict.

    Test if Accessor.get() returns correct results for an object,
    when used with a callable getter.
    """
    acc = Accessor(getter="value")
    assert acc.get(basic_dict) == basic_dict_value


@pytest.mark.parametrize(
    "basic_object_value",
    [
        {"key": {"key": lambda: "value"}},
        {"key": Obj(key="value")},
        Obj(key={"key": "value"}),
        Obj(key=Obj(key="value")),
    ],
)
def test_get_object_nested_dotted(basic_object, basic_object_value):
    """Test if accessor.get() correctly navigates nested values."""
    acc = Accessor(getter="value.key.key")
    assert acc.get(basic_object) == "value"
