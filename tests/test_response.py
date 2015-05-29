"""Tests for functions in atilla/response.py."""
import pytest
import werkzeug.exceptions

from atilla import response


def test_get_preferred_accepted_mimetype_with_hal_json(mock_request_context, mimetype):
    """Test that application/hal+json is prefered mimetype"""
    assert response.get_preferred_accepted_mimetype() == mimetype


@pytest.mark.parametrize("mimetype", ["application/json"])
def test_get_preferred_accepted_mimetype_with_json(mock_request_context):
    """Test that application/json is not prefered mimetype"""
    with pytest.raises(werkzeug.exceptions.NotAcceptable):
        response.get_preferred_accepted_mimetype()
