"""Basic objects and functions for testing."""
from collections import namedtuple

import pytest


VALUES = [
    'hello world',
    123456,
    {'hello': 'world'},
    ('hello', 'world'),
    ['hello', 'world'],
]

Obj = namedtuple('Obj', ['key'])


@pytest.fixture
def basic_object_value():
    """The value stored in the basic object."""
    return None


@pytest.fixture
def basic_object(basic_object_value):
    """Instance of basic_object."""
    class basic_object(object):

        """Simple object with one property."""

        def __init__(self, value=None):
            self.value = value

    return basic_object(value=basic_object_value)


@pytest.fixture
def basic_dict_value():
    """The value stored in the basic dict."""
    return None


@pytest.fixture
def basic_dict(basic_dict_value):
    """A basic dictionary."""
    return {'value': basic_dict_value}
