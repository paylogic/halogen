"""Test the serialize function of Schema."""
import mock

import halogen


@mock.patch.object(halogen.Attr, 'serialize')
def test_schema_calls_attr(attr_serialize):
    """Test that schema serialize calls attr serialize with the correct value."""
    class S(halogen.Schema):

        """Test schema."""

        key = halogen.Attr()

    S.serialize({'key': 1})
    attr_serialize.assert_called_once_with({'key': 1})


@mock.patch.object(halogen.Attr, 'serialize')
def test_schema_override_attr(attr_serialize):
    """Test that schema attributes can be overridden."""
    class S(halogen.Schema):

        """Test schema."""

        key = halogen.Attr()

    class T(S):

        """Test schema."""

        key = halogen.Attr()

    T.serialize({'key': 1})
    attr_serialize.assert_called_once_with({'key': 1})


def test_schema_override_attr_class():
    """Test that schema attributes can be overridden."""
    class S(halogen.Schema):

        """Test schema."""

        key = halogen.Attr()

    attr = halogen.Attr()

    class T(S):

        """Test schema."""

        key = attr

    assert T.__attrs__ == halogen.schema.OrderedDict(**{attr.name: attr})
