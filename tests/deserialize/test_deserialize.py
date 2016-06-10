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
