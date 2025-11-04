"""Test the basic functionality of the Accessor."""

from halogen.schema import Accessor


def test_accessor_repr():
    """Test Accessor repr."""
    acc = Accessor(getter="some.value", setter="some.other.value")
    assert repr(acc) == "<Accessor getter='some.value', setter='some.other.value'>"
