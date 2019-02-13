"""Test vnd.error."""

import uuid

import halogen
from halogen.vnd.error import Error, VNDError


class APIError(Error):

    def __init__(self, status_code, **kwargs):
        super(APIError, self).__init__(**kwargs)
        self.status_code = status_code
        self.logref = uuid.uuid4().hex


class AuthorSchema(halogen.Schema):

    name = halogen.Attr(required=True)


class PublisherSchema(halogen.Schema):

    name = halogen.Attr(required=True)
    address = halogen.Attr()


class BookSchema(halogen.Schema):

    title = halogen.Attr(required=True)
    year = halogen.Attr(halogen.types.Int(), required=True)
    authors = halogen.Attr(halogen.types.List(AuthorSchema), required=True)
    publisher = halogen.Attr(PublisherSchema)


def test_validation():
    try:
        BookSchema.deserialize(
            dict(
                # title is skipped
                year="abc",  # Not integer
                authors=[dict(name="John Smith"), dict()],  # Second author has no name
                publisher=dict(address="Chasey Lane 42, Los Angeles, US"),  # No name
            ),
        )
    except halogen.exceptions.ValidationError as e:
        error = APIError.from_validation_exception(e, status_code=400)

    assert error.status_code == 400

    data = VNDError.serialize(error)
    assert uuid.UUID(data["logref"])
    assert data["message"] == "Validation error."

    expected_errors = [
        dict(path="/authors/1/name", message="Missing attribute."),
        dict(path="/title", message="Missing attribute."),
        dict(path="/year", message="'abc' is not an integer"),
        dict(path="/publisher/name", message="Missing attribute."),
    ]
    expected = {e["path"]: e for e in expected_errors}
    errors = {e["path"]: e for e in data["_embedded"]["errors"]}

    assert errors.keys() == expected.keys()
    for path, exp in expected.items():
        err = errors[path]
        assert exp == dict(err)
