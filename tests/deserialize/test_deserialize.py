"""Test deserialize."""

import halogen


def test_attr_decorator_setter():
    """Test attribute as a decorator setter."""

    class Schema(halogen.Schema):

        @halogen.attr()
        def total(obj):
            return 123

        @total.setter
        def set_total(obj, value):
            obj['total'] = 321

    output = {}
    Schema.deserialize({"total": 555}, output=output)
    assert output["total"] == 321


def test_deserialize_kwargs():
    """Test that context is accessible in all attr variations"""

    class Schema(halogen.Schema):
        @halogen.attr()
        def total_decorator(obj, custom_kwarg):
            return obj['total'][custom_kwarg]

        @halogen.attr()
        def total_decorator_kwargs(obj, **kwargs):
            return obj['total'][kwargs['custom_kwarg']]

        total_lambda = halogen.Attr(attr=lambda obj, custom_kwarg: obj['total'][custom_kwarg])

        total_nested = halogen.Attr(
            halogen.Schema(nested=halogen.Attr(attr='mykey')),
            attr='total',
        )

        total_dot_sep_str = halogen.Attr(attr='total.mykey')

    deserialized = Schema.deserialize(
        {"total": {"mykey": 123}},
        custom_kwarg='mykey'
    )

    assert deserialized["total_decorator"] == 123
    assert deserialized["total_decorator_kwargs"] == 123
    assert deserialized["total_lambda"] == 123
    assert deserialized["total_nested"]["nested"] == 123
    assert deserialized["total_dot_sep_str"] == 123


def test_deserialize_kwargs_type():
    """Test that context is accessible in a type"""

    class Schema(halogen.Schema):
        @halogen.attr(halogen.types.ISOUTCDateTime())
        def datetime(obj, date):
            return '{}T{}Z'.format(date, obj['time'])

    deserialized = Schema.deserialize(
        {"time": "15:00:00"},
        date="2030-01-01"
    )

    assert deserialized["datetime"].isoformat() == '2030-01-01T15:00:00+00:00'


def test_deserialize_kwargs_list():
    """Test that context is maintained across a list"""

    class Book(halogen.Schema):
        @halogen.attr()
        def title(obj, language):
            return obj['title'][language]

    class Author(halogen.Schema):
        name = halogen.Attr(attr='author.name')
        books = halogen.Attr(
            halogen.types.List(Book),
            attr='author.books',
        )

    author = Author.deserialize({
        "author": {
            "name": "Roald Dahl",
            "books": [
                {
                    "title": {
                        "dut": "De Heksen",
                        "eng": "The Witches"
                    }
                },
                {
                    "title": {
                        "dut": "Sjakie en de chocoladefabriek",
                        "eng": "Charlie and the Chocolate Factory"
                    }
                }
            ]
        }
    }, language="eng")

    assert author == {
        "name": "Roald Dahl",
        "books": [
            {"title": "The Witches"},
            {"title": "Charlie and the Chocolate Factory"}
        ]
    }
