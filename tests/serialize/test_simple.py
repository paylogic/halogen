"""Tests for testing serialization of Halogen schemas."""

import halogen


def test_link_simple():
    """Check that link is serialized in the simple case."""
    data = {
        "uid": "/test/123",
    }

    class Schema(halogen.Schema):
        self = halogen.Link(attr="uid")

    assert Schema.serialize(data) == {"_links": {"self": {"href": "/test/123"}}}


def test_curies():
    """Check that curies are serialized in the simple case."""
    data = {
        "warehouse": "/test/123",
    }
    ACME = halogen.Curie(name="acme", href="/test/123")

    class Schema(halogen.Schema):

        """A test schema."""

        warehouse = halogen.Link(curie=ACME)

    assert Schema.serialize(data) == {
        "_links": {"curies": [{"name": "acme", "href": "/test/123"}], "acme:warehouse": {"href": "/test/123"}}
    }


def test_constant_href():
    """Test if serializing a constant attribute works correctly."""

    class Schema(halogen.Schema):

        """A test schema."""

        warehouse = halogen.Link("/test/123", deprecation="http://foo.bar")

    assert Schema.serialize({}) == {"_links": {"warehouse": {"deprecation": "http://foo.bar", "href": "/test/123"}}}


def test_attr_decorator_getter():
    """Test attribute as a decorator getter."""

    class Schema(halogen.Schema):
        @halogen.attr()
        def total(obj):
            return 123

    data = Schema.serialize({"total": 555})
    assert data["total"] == 123


def test_context():
    """Test passing context to serialize."""

    class Error(halogen.Schema):
        message = halogen.Attr(attr=lambda error, language: error["message"][language])

    error = Error.serialize(
        {"message": {"dut": "Ongeldig e-mailadres", "eng": "Invalid email address"}}, language="dut",
    )

    assert error == {"message": "Ongeldig e-mailadres"}
