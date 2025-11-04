"""Test the basic functionality of the Attr."""
from halogen.schema import Attr


def test_attr_repr():
    """Test Attr repr."""
    attr = Attr()
    attr.name = "some"
    assert repr(attr) == "<Attr 'some'>"


def test_attr_mutable_exclude():
    """Test that a list that is passed by reference is copied so that a shared reference is not kept."""
    exclude = ['a']
    attr = Attr(exclude=exclude)
    exclude.append('b')
    assert len(attr.exclude) == 1
