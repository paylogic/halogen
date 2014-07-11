"""Tests for the serialize function of Attr."""
import mock

from halogen.schema import Attr, Accessor
from halogen.types import Type


def test_serialize_type(mocked_get_context):
    """Test if serialization of a "type" works.

    Test if serialization of an Attr with an attr_type that is a "type" correctly calls the serialization function.
    """
    data = {"key": "value"}

    # The accessor should be used to get the value from data, so mock it, and check if it's been called at the end
    with mock.patch("halogen.schema.Attr.accessor", new_callable=mock.PropertyMock) as accessor:
        # Now that we've mocked the accessor property, we need to return a mocked Accessor, to check if its get()
        # is actually used.
        accessor_mock = mock.Mock(spec=Accessor)
        accessor_mock.get.return_value = "value"
        accessor.return_value = accessor_mock

        # Type holds the responsibility for serializing, so we need to mock Type, and check if its serialize()
        # is actually used.
        attr_type = mock.Mock(spec=Type)
        attr = Attr(attr_type=attr_type)
        attr.serialize(data)

    # Was the accessor used?
    accessor.assert_called_with()

    # Was the get() function of the accessor used?
    accessor_mock.get.assert_called_with(data)

    # Was the serialize function of the Type used to serialize the result of get?
    attr_type.serialize.assert_called_with("value")


def test_serialize_const():
    """Test if serialization of a constant works.

    Test if serialization of an Attr with an attr_type that is a constant correctly returns the constant.
    """
    data = {"key": "value"}

    with mock.patch("halogen.schema.Attr.accessor", new_callable=mock.PropertyMock) as accessor:
        accessor_mock = mock.Mock(spec=Accessor)
        accessor_mock.get.return_value = "value"
        accessor.return_value = accessor_mock

        attr_type = "constant"
        attr = Attr(attr_type=attr_type)
        assert attr.serialize(data) == "constant"

    # Since the attr_type is a constant, the accessor isn't needed. Make sure it wasn't called
    assert not accessor.called
