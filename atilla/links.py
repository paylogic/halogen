"""Utils for links."""

try:
    from urllib import parse as urlparse
except ImportError:  # pragma: no cover
    import urlparse
import urllib

from flask import current_app


def resolve_url_route(url):
    """Resolve a Flask URL route.

    :param url: `URL`.

    :return: `tuple` of a Flask endpoint and parsed URL parameters.

    :note: This function should be called in Flask application or request context.
    """
    # The real server name is not needed
    url_adapter = current_app.url_map.bind(server_name='')
    return url_adapter.match(urlparse.urlsplit(url).path)


def parse_url_parameters(uri):
    """Parse URI and get the URL parameters.

    :param uri: The resource `URI`.

    :return: A dictionary of the `URL` parameters contained in the `URI`.
    """
    name, parameters = resolve_url_route(uri)
    return parameters


def make_header_link(uri, rel):
    """Format a link according to the HTTP Link specification.

    :param uri: URI of the link.
    :param rel: Relation type.

    :return: A `URI` representing the `Link` header.
    """
    return u'{uri}; rel="{rel}"'.format(uri=uri, rel=rel)


def add_query_params(uri, new_params):
    """Append additional query params to a `URI`.

    :param uri: The `URI` to add query parameters to.
    :param new_params: A dictionary with the parameters to add or update.

    :return: A new `URI` containing query params.
    """
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(uri)
    query_params = dict(urlparse.parse_qsl(query, keep_blank_values=True))
    query_params.update(new_params)

    return urlparse.urlunparse(
        (
            scheme,
            netloc,
            path,
            params,
            urllib.urlencode(query_params),
            fragment,
        )
    )
