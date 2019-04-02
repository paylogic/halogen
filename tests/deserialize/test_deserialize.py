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
    assert deserialized["total_lambda"] == 123
    assert deserialized["total_nested"]["nested"] == 123
    assert deserialized["total_dot_sep_str"] == 123


def test_deserialize_kwargs_list():
    """Test that context is maintained across a list"""

    class Schema(halogen.Schema):
        @halogen.attr()
        def total(obj, custom_kwarg):
            return obj['total'][custom_kwarg]

    class ListSchema(halogen.Schema):
        deserialized_list = halogen.attr(halogen.types.List(Schema), attr='mylist')

    deserialized = ListSchema.deserialize(
        {
            "mylist": [
                {"total": {"mykey": 123}},
                {"total": {"mykey": 234}},
            ]
        },
        custom_kwarg='mykey'
    )

    assert deserialized['deserialized_list'] == [
        {"total": 123},
        {"total": 234},
    ]
