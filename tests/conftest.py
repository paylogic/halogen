"""Test configuration."""

import halogen
import mock
import pytest
from .fixtures.common import *


@pytest.fixture(scope="session")
def mocked_get_context():
    """Mock halogen.schema._get_context for returning empty dict."""
    patcher = mock.patch("halogen.schema._get_context")
    patcher.start()
    patcher.return_value = {}
