"""Test serialization with defaults."""

import pytest

import halogen


def test_serialize_required_default_simple():
    """Test serialization with defaults."""
    class Schema(halogen.Schema):

        attr = halogen.Attr(required=True, default=1)

    serialized = Schema.serialize({})
    assert serialized == {'attr': 1}


def test_serialize_required_default_lambda():
    """Test serialization with defaults."""
    class Schema(halogen.Schema):

        attr = halogen.Attr(required=True, default=lambda: 'lambda')

    serialized = Schema.serialize({})
    assert serialized == {'attr': 'lambda'}


def test_serialize_required_no_default():
    """Test serialization with defaults."""
    class Schema(halogen.Schema):

        attr = halogen.Attr(required=True)

    with pytest.raises(KeyError):
        Schema.serialize({})


def test_serialize_not_required_default():
    """Test serialization with defaults."""
    class Schema(halogen.Schema):

        attr = halogen.Attr(required=False, default=1)

    serialized = Schema.serialize({})
    assert serialized == {'attr': 1}


def test_serialize_not_required_no_default():
    """Test serialization with defaults."""
    class Schema(halogen.Schema):

        attr = halogen.Attr(required=False)

    serialized = Schema.serialize({})
    assert serialized == {}
