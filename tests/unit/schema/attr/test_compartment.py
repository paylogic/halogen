"""Tests for the compartment property of Attr."""

from halogen.schema import Attr


def test_compartment():
    """Test if the default compartment is None."""
    attr = Attr()
    assert attr.compartment is None
