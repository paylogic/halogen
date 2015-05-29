"""Tests for validators."""

import pytest
import uuid
import werkzeug.exceptions

from atilla import validators


def test_uid_validator():
    """Check that UidValidator not fail with normal uuid."""
    random_uuid = str(uuid.uuid4())
    uid_validator = validators.UidValidator({})
    assert uid_validator.to_python(random_uuid) == random_uuid


def test_uid_validator_raises_exception():
    """Check that UidValidator not fail with normal uuid."""
    uid_validator = validators.UidValidator({})
    with pytest.raises(werkzeug.exceptions.BadRequest):
        uid_validator.to_python('wrong_uuid')
