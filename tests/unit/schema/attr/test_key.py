"""Tests for the key property of Attr."""

from halogen.schema import Attr


def test_key():
    """Test if the key property uses the name attribute."""
    attr = Attr()
    attr.name = 'value'
    assert attr.key == 'value'
