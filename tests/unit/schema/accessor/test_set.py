"""Test the functionality of the Accessor schema."""

import mock
import pytest

from halogen.schema import Accessor

from tests.fixtures.common import Obj, VALUES


def basic_set_object(obj, value):
    """Set the value of attribute "value" of "obj"."""
    obj.value = value


def basic_set_dict(dic, value):
    """Set the value of attribute "value" of "obj"."""
    dic["value"] = value


@pytest.mark.parametrize("basic_object_value", VALUES)
def test_set_object_callable(basic_object, basic_object_value):
    """Test if Accessor.set() sets the value of an object when setter is callable."""
    acc = Accessor(setter=basic_set_object)
    acc.set(basic_object, "")
    assert basic_object.value == ""

    acc.set(basic_object, basic_object_value)
    assert basic_object.value == basic_object_value


def test_set_object_callable_called(basic_object):
    """Test if Accessor.set() calls Accessor.setter() if setter is callable."""
    acc = Accessor()
    acc.setter = mock.Mock()
    acc.set(basic_object, "")

    acc.setter.assert_called_once_with(basic_object, "")


@pytest.mark.parametrize("basic_object_value", VALUES)
def test_set_object_string(basic_object, basic_object_value):
    """Test if Accessor.set() sets the value of an object when setter is a string."""
    acc = Accessor(setter="value")
    acc.set(basic_object, "")
    assert basic_object.value == ""

    acc.set(basic_object, basic_object_value)
    assert basic_object.value == basic_object_value


@pytest.mark.parametrize("basic_dict_value", VALUES)
def test_set_dict_callable(basic_dict, basic_dict_value):
    """Test if Accessor.set() sets the value of an dict if setter is callable."""
    acc = Accessor(setter=basic_set_dict)
    acc.set(basic_dict, "")
    assert basic_dict["value"] == ""

    acc.set(basic_dict, basic_dict_value)
    assert basic_dict["value"] == basic_dict_value


@pytest.mark.parametrize("basic_dict_value", VALUES)
def test_set_dict_string(basic_dict, basic_dict_value):
    """Test if setting values in a dict works if setter is a string."""
    acc = Accessor(setter="value")
    acc.set(basic_dict, "")
    assert basic_dict["value"] == ""

    acc.set(basic_dict, basic_dict_value)
    assert basic_dict["value"] == basic_dict_value


@pytest.mark.parametrize(
    "basic_object_value",
    [{"key": {"key": "value"}}, {"key": Obj(key="value")}, Obj(key={"key": "value"}), Obj(key=Obj(key="value"))],
)
def test_set_object_nested_dotted(basic_object, basic_object_value):
    """Test if accessor.get() correctly navigates nested values."""
    acc = Accessor(getter="value.key.key", setter="value.key.key")

    acc.set(basic_object, "")
    assert acc.get(basic_object) == ""

    acc.set(basic_object, "value")
    assert acc.get(basic_object) == "value"
