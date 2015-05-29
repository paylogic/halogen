"""Test exception handlers."""

try:
    from http import client as httplib
except ImportError:  # pragma: no cover
    import httplib
import halogen
import flask


class MySchema(halogen.Schema):

    """Test schema."""

    num = halogen.Attr(halogen.types.Int(validators=[halogen.validators.Range(min=10, max=11)]))


def test_deserialize(application, http):
    """Test validation errors are rendered."""
    @application.route('/')
    def index():
        flask.request.deserialize(MySchema)
        return 'OK'

    response = http.get(
        '/',
        query_string=dict(num=1),
    )
    assert response.status_code == httplib.BAD_REQUEST
    data = response.parsed_data

    assert data['message'] == 'Bad request.'
    assert 'details' in data
    assert 'logref' in data
    assert data['type'] == 'BAD_REQUEST'
    assert application.db._rolledback


def test_unhandled(application, http):
    """Test unhandled exception is being handled."""
    @application.route('/')
    def index():
        1 / 0

    response = http.get('/')
    assert response.status_code == httplib.INTERNAL_SERVER_ERROR
    data = response.parsed_data
    assert 'by zero' in data['message']
    assert 'logref' in data
    assert data['type'] == 'UNKNOWN_ERROR'
    assert application.db._rolledback


def test_unhandled_object(application, http):
    """Test unhandled exception with object as message."""
    @application.route('/')
    def index():

        class SomeObject(object):

            """Some object."""

            def __init__(self, attr):
                self.attr = attr

        raise Exception(SomeObject(1))

    response = http.get('/')
    assert response.status_code == httplib.INTERNAL_SERVER_ERROR
    data = response.parsed_data
    assert data['message'].startswith('Exception: <tests.test_exceptions.')
    assert 'logref' in data
    assert data['type'] == 'UNKNOWN_ERROR'
    assert application.db._rolledback
