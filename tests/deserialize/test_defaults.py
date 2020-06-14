"""Test deserialization with defaults."""

import pytest

import halogen


def test_deserialize_required_default_simple():
    """Test deserialization with defaults."""

    class Schema(halogen.Schema):

        attr = halogen.Attr(required=True, default=1)

    deserialized = Schema.deserialize({})
    assert deserialized == {"attr": 1}


def test_deserialize_required_default_lambda():
    """Test deserialization with defaults."""

    class Schema(halogen.Schema):

        attr = halogen.Attr(required=True, default=lambda: "lambda")

    deserialized = Schema.deserialize({})
    assert deserialized == {"attr": "lambda"}


def test_deserialize_required_no_default():
    """Test deserialization with defaults."""

    class Schema(halogen.Schema):

        attr = halogen.Attr(required=True)

    with pytest.raises(halogen.exceptions.ValidationError):
        Schema.deserialize({})


def test_deserialize_not_required_default():
    """Test deserialization with defaults."""

    class Schema(halogen.Schema):

        attr = halogen.Attr(required=False, default=1)

    deserialized = Schema.deserialize({})
    assert deserialized == {"attr": 1}


def test_deserialize_not_required_no_default():
    """Test deserialization with defaults."""

    class Schema(halogen.Schema):

        attr = halogen.Attr(required=False)

    deserialized = Schema.deserialize({})
    assert deserialized == {}
