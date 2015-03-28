"""Test the basic functionality of the Attr."""
from halogen.schema import Attr


def test_attr_repr():
    """Test Attr repr."""
    attr = Attr()
    attr.name = 'some'
    assert repr(attr) == "<Attr 'some'>"
