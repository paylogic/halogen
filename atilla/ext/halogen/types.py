"""Schema types."""
import six

import werkzeug.exceptions
import flask
import halogen
import halogen.exceptions

from atilla import links


class URI(halogen.types.Type):

    """Resource id to URI conversion type."""

    def __init__(self, endpoint, external=True):
        """`URI` type constructor.

        :param endpoint: Flask route endpoint name to compare with when specified.
        :param external: Is URI external (include schema and domain).
        """
        self.endpoint = endpoint
        self.external = external
        super(URI, self).__init__()

    def serialize(self, value):
        """Convert resource id to :ref:`URI`.

        :param value: Resource id value.
        :return: :ref:`URI`.
        """
        if not isinstance(value, dict):
            value = {'uid': value}

        return flask.url_for(self.endpoint, _external=self.external, **value)

    def deserialize(self, value):
        """Parse :ref:`URI` and get resource id.

        :param value: :ref:`URI` value.
        :return: Converted resource id.
        """
        if not isinstance(value, six.string_types):
            raise ValueError(u"'{val}' is not a valid URI".format(val=value))
        try:
            endpoint, params = links.resolve_url_route(value)
            if self.endpoint:
                assert endpoint == self.endpoint
        except (RuntimeError, AssertionError):  # Re-raise the Flask context exception
            raise
        except werkzeug.exceptions.HTTPException as e:
            raise ValueError(
                u"'{val}' is not a valid URI for the '{endpoint}' endpoint: {err}".format(
                    val=value,
                    endpoint=self.endpoint,
                    err=e,
                )
            )
        try:
            return params.values()[0] if len(params) == 1 else params
        except (TypeError, IndexError):
            raise ValueError(u'Could not parse the URI parameters {0}.'.format(unicode(params)))
