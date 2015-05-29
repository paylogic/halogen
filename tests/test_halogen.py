"""Tests for halogen types."""
import pytest

import halogen

from atilla.ext.halogen import types


class Ticket(halogen.Schema):

    """Test schema."""

    item = halogen.Attr(
        types.URI('static'),
    )


def test_uri(current_app):
    """Test URI schema type."""
    with pytest.raises(halogen.exceptions.ValidationError) as err:
        Ticket.deserialize({'item': ''})
    assert err.value.errors[0].errors[0].args[0] == "'' is not a valid URI for the 'static' endpoint: 404: Not Found"

    with pytest.raises(halogen.exceptions.ValidationError) as err:
        Ticket.deserialize({'item': {}})
    assert err.value.errors[0].errors[0].args[0] == "'{}' is not a valid URI"
