"""Test configuration."""
import mock


from halogen.schema import getargspec
from .fixtures.common import *


@pytest.fixture(scope="session")
def mocked_inspect_getargspec(request):
    """Mock halogen.schema._get_context for returning empty dict."""
    def f():
        return None

    patcher = mock.patch("inspect.getargspec")
    patcher.return_value = getargspec(f)

    patcher.start()
    request.addfinalizer(patcher.stop)
