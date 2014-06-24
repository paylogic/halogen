import mock

import halogen


@mock.patch.object(halogen.Attr, 'serialize')
def test_schema_calls_attr(attr_serialize):
    """Test that schema serialize calls attr serialize with the correct value."""
    class S(halogen.Schema):
        key = halogen.Attr()

    S.serialize({'key': 1})
    attr_serialize.assert_called_once_with({'key': 1})
