"""All response related utility functions."""

import logging
try:
    from http import client as httplib
except ImportError:  # pragma: no cover
    import httplib
import json
import uuid

import six

import halogen
from flask import request, abort, current_app, make_response
try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict


MIMETYPE_SERIALIZER = OrderedDict([
    (
        'application/hal+json',
        lambda context: json.dumps(context, indent=4, sort_keys=True)
    ),
])


def api_response(content, status_code=None, headers=None):
    """API response handler.

    :note: The contents are encoded according to the request's accepted mimetype.

    :param content: Response body.
    :param status_code: HTTP status code.
    :param headers: Headers.

    :return: A tuple with `contents`, `status_code`, `headers`.
    """
    mimetype = get_preferred_accepted_mimetype()
    all_headers = set_basic_headers(request, mimetype=mimetype)

    if headers:
        all_headers.update(headers)
    serializer = MIMETYPE_SERIALIZER[mimetype]
    body = serializer(content) if content is not None else ''
    return body, status_code, all_headers


def get_preferred_accepted_mimetype():
    """Return the request's accepted mimetype.

    If the request accepts more than one, it returns the one that appears first on MIMETYPE_SERIALIZER.
    """
    for mimetype, serializer in MIMETYPE_SERIALIZER.items():
        if mimetype in request.accept_mimetypes:
            return mimetype

    abort(
        httplib.NOT_ACCEPTABLE,
        u'The only accepted mimetypes are {0}'.format(', '.join(MIMETYPE_SERIALIZER.keys()))
    )


def get_current_profile_link(*args, **kwargs):
    """Get the profile link from the current endpoint."""
    try:
        schema = current_app.view_functions[request.endpoint].schema
        profile = next((attr for attr in schema.__attrs__ if attr.name == 'profile'))
        return profile.serialize(None)['href']
    except (KeyError, AttributeError, StopIteration):
        return None


def get_error_message(exception):
    """Get the exception message.

    :param exception: Exception object.
    :return: Exception message or description.
    :raises AttributeError: when the message is not available.
    """
    message = getattr(exception, 'message', None)
    if not message:
        message = exception.description
    if not isinstance(message, six.string_types):
        message = u'{0}: {1}'.format(exception.__class__.__name__, message)
    return message


class VNDError(halogen.Schema):

    """An exception that can be serialized to the hal+json format."""

    message = halogen.Attr(required=False, attr=get_error_message)
    logref = halogen.Attr(attr=lambda error: uuid.uuid4().hex)
    help = halogen.Link(required=False, attr=get_current_profile_link)

    # Extended fields
    type = halogen.Attr(required=False, attr='error_type', default='UNKNOWN_ERROR')
    """Error type identifier."""

    details = halogen.Attr(required=False, attr='data')
    """Optional additional error details."""


def vnd_error_response(exception, status_code=None, headers=None):
    """API error response handler.

    If there is an uncaught internal server error it is logged and sent to sentry.
    It is not shown to the users and is not passed along, in essence: it disappears hereafter.

    :param exception: Exception raised in the request/response cycle.
    :param status_code: HTTP status code.
    :param headers: Extra response headers.

    :return: vnd.error response with the error details.
    """
    all_headers = set_basic_headers(request, mimetype='application/hal+json')
    if headers:
        all_headers.update(headers)
    if not hasattr(exception, 'message'):
        try:
            exception.message = exception.args[0]
        except IndexError:
            exception.message = ''
    body = VNDError.serialize(exception)

    if status_code == httplib.INTERNAL_SERVER_ERROR or current_app.config['SENTRY_CAPTURE_USER_ERRORS']:
        sentry = getattr(current_app, 'sentry', None)
        if sentry:
            sentry.captureException()

    if status_code == httplib.INTERNAL_SERVER_ERROR:
        log_exception = True
        exc_info = True
        level = logging.ERROR
    else:
        log_exception = current_app.config['LOG_USER_ERRORS']
        exc_info = current_app.config['LOG_USER_ERROR_EXC_INFO']
        level = current_app.config['LOG_USER_ERROR_LEVEL']

    if log_exception:
        current_app.logger.log(level, u"{type} {logref} {body}".format(body=body, **body), exc_info=exc_info)

    response = make_response(json.dumps(body), status_code)
    response.headers = all_headers
    return response


def set_basic_headers(request, mimetype=None):
    """Set the basic headers for API response.

    :param methods: a wildcard or a list of allowed HTTP methods.
    :param mimetype: a string representing the mimetype to use to render text.

    :return: a dictionary with basic headers.
    """
    headers = {
        'Access-Control-Allow-Headers': ['Content-Type', 'Authorization', 'Accept', 'X-Requested-With'],
        'Access-Control-Expose-Headers': ['Link'],
    }
    if mimetype:
        headers['Content-Type'] = mimetype

    url_adapter = current_app.url_map.bind(server_name=current_app.config['SERVER_NAME'])
    methods = url_adapter.allowed_methods(request.path)

    headers['Access-Control-Allow-Methods'] = methods
    headers['Allow'] = methods

    # check the referer because of PREFLIGHT OPTIONS or other AJAX requests
    referer = request.headers.get('Referer')
    if referer:
        origin = request.headers.get('Origin')
        headers['Access-Control-Allow-Credentials'] = 'true'
    else:
        origin = '*'

    headers['Access-Control-Allow-Origin'] = origin

    return headers
