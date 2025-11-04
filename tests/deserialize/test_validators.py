"""Test deserialization with defaults."""

import pytest

import halogen


@pytest.fixture(params=[False, True])
def lazy(request):
    return request.param


def test_less_than(lazy):
    """Test less than validator."""

    class Schema(halogen.Schema):

        attr = halogen.Attr(
            halogen.types.Type(
                validators=[
                    halogen.validators.LessThanEqual((lambda: 1) if lazy else 1, value_err="{0} is bigger than {1}"),
                ]
            )
        )

    with pytest.raises(halogen.exceptions.ValidationError) as err:
        Schema.deserialize({"attr": 2})
    assert "2 is bigger than 1" in str(err.value)

    assert Schema.deserialize({"attr": 1}) == {"attr": 1}


def test_greated_than(lazy):
    """Test greater than validator."""

    class Schema(halogen.Schema):

        attr = halogen.Attr(
            halogen.types.Type(
                validators=[
                    halogen.validators.GreatThanEqual((lambda: 1) if lazy else 1, value_err="{0} is smaller than {1}")
                ]
            )
        )

    with pytest.raises(halogen.exceptions.ValidationError) as err:
        Schema.deserialize({"attr": 0})
    assert "0 is smaller than 1" in str(err.value)
    assert Schema.deserialize({"attr": 1}) == {"attr": 1}


def test_length(lazy):
    """Test length validator."""

    class Schema(halogen.Schema):

        attr = halogen.Attr(
            halogen.types.Type(
                validators=[
                    halogen.validators.Length(
                        (lambda: 1) if lazy else 1,
                        (lambda: 2) if lazy else 2,
                        min_err="Length is less than {0}",
                        max_err="Length is greater than {0}",
                    )
                ]
            )
        )

    with pytest.raises(halogen.exceptions.ValidationError) as err:
        Schema.deserialize({"attr": []})
    assert "Length is less than 1" in str(err.value)

    with pytest.raises(halogen.exceptions.ValidationError) as err:
        Schema.deserialize({"attr": 1})
    assert "Length is less than 1" in str(err.value)

    with pytest.raises(halogen.exceptions.ValidationError) as err:
        Schema.deserialize({"attr": [1, 2, 3]})
    assert "Length is greater than 2" in str(err.value)


def test_range(lazy):
    """Test range validator."""

    class Schema(halogen.Schema):

        attr = halogen.Attr(
            halogen.types.Type(
                validators=[
                    halogen.validators.Range(
                        1,
                        2,
                        min_err="{val} is less than minimum value {min}",
                        max_err="{val} is greater than maximum value {max}",
                    )
                ]
            )
        )

    with pytest.raises(halogen.exceptions.ValidationError) as err:
        Schema.deserialize({"attr": 0})
    assert "0 is less than minimum value 1" in str(err.value)

    with pytest.raises(halogen.exceptions.ValidationError) as err:
        Schema.deserialize({"attr": 3})
    assert "3 is greater than maximum value 2" in str(err.value)


def test_one_of():
    class Schema(halogen.Schema):

        attr = halogen.Attr(halogen.types.Type(validators=[halogen.validators.OneOf([1, 2, 3])]))

    with pytest.raises(halogen.exceptions.ValidationError) as err:
        Schema.deserialize({"attr": 4})
    assert '\\"4\\" is not a valid choice' in str(err.value)

    Schema.deserialize({"attr": 3})
