"""Flask request and response wrappers."""

try:
    from http import client as httplib
except ImportError:  # pragma: no cover
    import httplib
import json
import halogen

from flask import Request as RequestBase, Response as ResponseBase, abort
from werkzeug.utils import cached_property
from atilla import exceptions


def parse_data(data, mimetype, charset=None):
    """Parse the request/response data.

    :param data: Serialized data.
    :param mimetype: MIME type of the data (only json is supported).
    :param charset: Character set used for the serialization. Default if None.
    :raises: `ValueError` when the data can't be parsed.

    :return: Python objects.
    """
    if data == '' or data is None:
        return

    JSON_MIMETYPES = (
        'application/json',
        'application/hal+json',
    )

    if mimetype in JSON_MIMETYPES:
        if charset is not None:
            return json.loads(data, encoding=charset)
        else:
            return json.loads(data)
    else:
        raise ValueError('Mimetype is not supported')


class Request(RequestBase):

    """Request object used by default in the API.

    The request object is a :class:`flask.wrappers.Request` subclass
    and provides all of the attributes Flask and Werkzeug define plus
    a few API specific ones.
    """

    @cached_property
    def api_key(self):
        """Get the api key."""
        return self.authorization.get('username') if self.authorization else None

    @cached_property
    def parsed_data(self):
        """Parsed the payload data.

        :return: Python object (or list) representing the request payload.

        :raises: Aborts the request with the BAD_REQUEST error.
        """
        try:
            return parse_data(
                data=self.get_data(),
                mimetype=self.mimetype,
                charset=self.mimetype_params.get('charset'),
            )
        except (ValueError, LookupError):
            abort(httplib.BAD_REQUEST, 'The payload could not be parsed')

    @cached_property
    def parsed_form(self):
        """Request form with the list values."""
        if self.method in ('POST', 'PUT'):
            params = self.parsed_data
        else:
            params = {}
            for key, value in self.args.items(multi=True):
                if key in params:
                    param = params.get(key)
                    if isinstance(param, list):
                        param.append(value)
                    else:
                        params[key] = [param, value]
                else:
                    params[key] = value
        return params

    def deserialize(self, schema_class):
        """Deserialize the request data with the schema and validate.

        :param schema_class: Schema class to use for the deserialization and validation.
        :raise: `ValidationError` in case the data doesn't pass the schema validation.
        :return: Deserialized data.
        """
        try:
            return schema_class.deserialize(self.parsed_form or {})
        except halogen.exceptions.ValidationError as e:
            raise exceptions.BadRequest(message='Bad request.', errors=e.to_dict())


class Response(ResponseBase):

    """Response object used by default in the API tests.

    The response object is a :class:`flask.wrappers.Response` subclass
    and provides all of the attributes Flask and Werkzeug define plus
    a few API specific ones.
    """

    @cached_property
    def parsed_data(self):
        """Parsed the response data.

        :return: Python object (or list) representing the request payload.

        :raises: Aborts the request with the BAD_REQUEST error.
        """
        return parse_data(
            data=self.get_data().decode(self.mimetype_params.get('charset', 'utf-8')),
            mimetype=self.mimetype,
            charset=self.mimetype_params.get('charset'),
        )
