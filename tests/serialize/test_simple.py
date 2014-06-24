"""Tests for testing serialization of Halogen schemas."""

import halogen


def test_link_simple():
    """Check that link is serialized in the simple case."""

    data = {
        "uid": "/test/123",
    }

    class Schema(halogen.Schema):
        self = halogen.Link(attr="uid")

    assert Schema.serialize(data) == {
        "_links": {
            "self": {"href": "/test/123"}
        }
    }


def test_curies():

    data = {
        "warehouse": "/test/123",
    }
    ACME = halogen.Curie(name="acme", href="/test/123")

    class Schema(halogen.Schema):
        warehouse = halogen.Link(curie=ACME)

    assert Schema.serialize(data) == {
        "_links": {
            "curies": [{
                "name": "acme",
                "href": "/test/123",
            }],
            "acme:warehouse": {"href": "/test/123"},
        }
    }


def test_constant_href():

    class Schema(halogen.Schema):

        warehouse = halogen.Link("/test/123")

    assert Schema.serialize({}) == {
        "_links": {
            "warehouse": {"href": "/test/123"},
        }
    }
