"""Test client.

Example usage:

    with app.test_client() as c:
        # Add the content type and authorization headers here
        c.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = c.get(url)
"""
from six.moves.urllib import parse as urlparse

from flask import url_for
from flask.testing import FlaskClient


class TestClient(FlaskClient):

    """Flask test client."""

    def open(self, url, *args, **kwargs):
        """Override the open to inject the headers."""
        # Bug in the werkzeug? When the scheme and netloc is present the querystring is ignored
        result = urlparse.urlsplit(url)
        url = urlparse.urlunsplit(('', '', result.path, result.query, result.fragment))

        headers = getattr(self, 'headers', None)
        if headers is not None:
            kwargs.setdefault('headers', headers)
        return super(TestClient, self).open(url, *args, **kwargs)

    def make_uri(self, *args, **kwargs):
        """Reverse the URL in the application context.

        :note: Requires SERVER_NAME to be defined in the configuration.

        """
        with self.application.app_context():
            return url_for(*args, _external=True, **kwargs)
