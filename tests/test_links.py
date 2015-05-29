"""Tests for functions in atilla/links.py."""
import pytest
from werkzeug import exceptions
from atilla import links


def test_resolve_url_route(current_app):
    """Test resolving a Flask URL route."""

    assert links.resolve_url_route('http://127.0.0.1:8000/static/favicon.ico') == (
        'static', {'filename': 'favicon.ico'}
    )

    with pytest.raises(exceptions.NotFound):
        assert links.resolve_url_route('http://127.0.0.1:8000/shouldnotbefound')


def test_parse_url_parameters(current_app):
    """Test parse URI with the UIDs."""
    uid = 'favicon.ico'
    uri = 'http://127.0.0.1:8000/static/{0}'.format(uid)

    assert links.parse_url_parameters(uri) == {'filename': uid}

    with pytest.raises(exceptions.NotFound):
        assert links.parse_url_parameters('http://127.0.0.1:8000/shouldnotbefound')


def test_make_header_link():
    """Format a link according to the HTTP Link specification."""
    uri = 'http://127.0.0.1:8000/shouldnotbefound'
    rel = 'norel'
    assert links.make_header_link(uri, rel) == u'{uri}; rel="{rel}"'.format(uri=uri, rel=rel)
