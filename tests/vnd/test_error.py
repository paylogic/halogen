# coding=utf8
"""Test vnd.error."""


import json
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
                year="☃bc",  # Not an integer
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
        dict(path="/publisher/name", message="Missing attribute."),
        dict(path="/title", message="Missing attribute."),
        dict(path="/year", message="'☃bc' is not an integer"),
    ]

    assert data["errors"] == expected_errors


def test_to_dict():
    error = Error(message="Something went wrong", path="/foo")
    result = error.to_dict()
    assert result == {"message": "Something went wrong", "path": "/foo"}


def test_to_dict_with_nested_errors():
    error = Error(
        message="Validation error.",
        errors=[
            Error(message="Missing attribute.", path="/title"),
            Error(message="Not an integer", path="/year"),
        ],
    )
    result = error.to_dict()
    assert result["message"] == "Validation error."
    assert result["errors"] == [
        {"message": "Missing attribute.", "path": "/title"},
        {"message": "Not an integer", "path": "/year"},
    ]


def test_to_json():
    error = Error(message="Something went wrong", path="/foo")
    result = error.to_json()
    assert json.loads(result) == {"message": "Something went wrong", "path": "/foo"}


def test_to_json_roundtrip():
    try:
        BookSchema.deserialize(
            dict(
                year="abc",
                authors=[dict(name="John Smith"), dict()],
                publisher=dict(address="Chasey Lane 42"),
            ),
        )
    except halogen.exceptions.ValidationError as e:
        error = Error.from_validation_exception(e)

    result = json.loads(error.to_json())
    assert result["message"] == "Validation error."
    assert len(result["errors"]) == 4
