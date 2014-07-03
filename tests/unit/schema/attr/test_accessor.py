"""Tests the accessor property of the Attr schema."""

from halogen.schema import Attr, Accessor


def test_accessor_accessor():
    """Test if accessor returns the correct Accessor object when the attr property is an accessor."""
    attr = Attr()
    attr.name = 'name'
    acc = Accessor()
    attr.attr = acc

    assert attr.accessor == acc


def test_accessor_string():
    """Test if accessor returns the correct Accessor object when the attr property is a string."""
    attr = Attr()
    attr.name = 'name'
    attr.attr = 'attribute'

    acc = attr.accessor
    assert isinstance(acc, Accessor)
    assert acc.getter == attr.attr
    assert acc.setter == attr.attr


def test_accessor_callable():
    """Test if accessor returns the correct Accessor object when the attr property is a callable."""
    attr = Attr()
    attr.name = 'name'
    attr.attr = lambda x: x

    acc = attr.accessor
    assert isinstance(acc, Accessor)
    assert acc.getter == attr.attr
    assert acc.setter is None


def test_accessor_name():
    """Test if accessor returns the correct Accessor object when the attr property is Falsy."""
    attr = Attr()
    attr.name = 'name'
    attr.attr = None

    acc = attr.accessor
    assert isinstance(acc, Accessor)
    assert acc.getter == attr.name
    assert acc.setter == attr.name
