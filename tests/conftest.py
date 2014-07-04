"""Test configuration."""

import halogen
import mock
import pytest
from fixtures.common import *


@pytest.fixture(scope="session")
def mock_get_context():
    patcher = mock.patch("halogen.schema._get_context")
    patcher.start()
    patcher.return_value = {}
