"""Test configuration."""
import mock
import pytest
from flask.ctx import RequestContext
from flask.wrappers import Request

from atilla.server import create_app


class TestDBSessionManager(object):

    """Test DB session manager."""

    _commited = False
    _rolledback = False
    _closed = False

    do_commit = False

    def commit(self):
        """Mark as committed."""
        self._commited = True

    def close(self):
        """Mark as closed."""
        self._closed = True

    def rollback(self):
        """Mark as rolled back."""
        self._rolledback = True


@pytest.fixture()
def application(mocked_memcached):
    """Atilla Flask test application."""
    app = create_app(
        name='tests',
        mode='test',
        settings_module='tests.settings',
    )
    app.db = TestDBSessionManager()
    return app


@pytest.yield_fixture
def current_app(request, application):
    """Mocking flask.current_app."""
    with application.app_context():
        yield application


@pytest.fixture
def mimetype():
    """Response mimetype."""
    return 'application/hal+json'


@pytest.fixture
def mock_request_context(request, application, mimetype):
    """Mocking flask.current_app."""
    from flask.testing import make_test_environ_builder

    builder = make_test_environ_builder(application)
    environ = builder.get_environ()

    flask_request = Request(environ)
    flask_request.accept_mimetypes = [mimetype]
    request_context = RequestContext(application, environ, request=flask_request)
    request_context.__enter__()

    request.addfinalizer(lambda: request_context.__exit__(None, None, None))


@pytest.yield_fixture
def mocked_memcached():
    """Mocked memcached."""
    mocked = mock.patch('memcache.Client')
    yield mocked.start()
    mocked.stop()


@pytest.fixture
def http(application):
    """Test client.

    Usage:
        with http as c:
            response = c.get(uri)
            print response.parsed_data
    """
    return application.test_client()
