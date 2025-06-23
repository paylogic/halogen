import pytest

import halogen
from halogen.exceptions import InvalidSchemaDefinition


def test_invalid_embedded_validation():
    class EmbeddedWithoutSelfReferenceSchema(halogen.Schema):
        name = halogen.types.String()

    class ValidEmbeddedSchema(halogen.Schema):
        self = halogen.Link()

    with pytest.raises(InvalidSchemaDefinition):
        class TestSchema(halogen.Schema):
            embedded_value = halogen.Embedded(EmbeddedWithoutSelfReferenceSchema)

    with pytest.raises(InvalidSchemaDefinition):
        class TestWithInvalidListSchema(halogen.Schema):
            embedded_value = halogen.Embedded(halogen.types.List(halogen.types.String))

    with pytest.raises(InvalidSchemaDefinition):
        class TestWithEmptyListSchema(halogen.Schema):
            embedded_value = halogen.Embedded(halogen.types.List())

    with pytest.raises(InvalidSchemaDefinition):
        class TestWithIncorrectValueSchema(halogen.Schema):
            embedded_value = halogen.Embedded(halogen.types.String())


def test_valid_embedded_validation():
    class EmbeddedWithSelfReferenceSchema(halogen.Schema):
        self = halogen.Link()

    class EmbeddedWithSelfReferenceFunctionSchema(halogen.Schema):

        @halogen.Link()
        def self(self):
            return "/foobar/1"

    class NestedEmbeddedReferenceSchema(EmbeddedWithSelfReferenceSchema):
        name = halogen.Attr(halogen.types.String())

    class TestSchema(halogen.Schema):
        embedded_value = halogen.Embedded(EmbeddedWithSelfReferenceSchema)

    class TestWithFunctionSchema(halogen.Schema):
        embedded_value = halogen.Embedded(EmbeddedWithSelfReferenceFunctionSchema)

    class TestWithListSchema(halogen.Schema):
        embedded_value = halogen.Embedded(halogen.types.List(EmbeddedWithSelfReferenceFunctionSchema))
