"""Halogen schema primitives."""

import sys

from . import types
from . import exceptions

PY2 = sys.version_info[0] == 2

if not PY2:
    string_types = (str,)
else:
    string_types = (str, unicode)


BYPASS = lambda value: value


class Accessor(object):

    """Object that incapsulates the getter and the setter of the attribute."""

    def __init__(self, getter=None, setter=None):
        self.getter = getter
        self.setter = setter

    def get(self, value):
        """Get an attribute from a value.

        :param value: Object to get the attribute value from.
        :return: Value of object's attribute.
        """
        assert self.getter is not None, "Getter accessor is not specified."
        if callable(self.getter):
            return self.getter(value)

        assert isinstance(self.getter, string_types), "Accessor must be a function or a dot-separated string."

        for attr in self.getter.split("."):
            if isinstance(value, dict):
                value = value[attr]
            else:
                value = getattr(value, attr)

        if callable(value):
            return value()

        return value

    def set(self, result, value):
        """Set value for result's attribute.

        :param result: Result object or dict to assign the attribute to.
        :param value: Value to be assigned.
        """
        assert self.setter is not None, "Setter accessor is not specified."
        if callable(self.setter):
            return self.setter(value)

        assert isinstance(self.setter, string_types), "Accessor must be a function or a dot-separated string."

        def setdefault(result, attr, value):
            if isinstance(result, dict):
                result.setdefault(attr, value)
            else:
                setattr(result, attr, value)
            return value

        path = self.setter.split(".")
        for attr in path[:-1]:
            result = setdefault(result, attr, {})
        setdefault(result, path[-1], value)

    def __repr__(self):
        """Accessor representation."""
        return "<{0} getter='{1}', setter='{1}'>".format(
            self.__class__.__name__,
            self.getter,
            self.setter,
        )


class Attr(object):

    """Schema attribute."""

    def __init__(self, attr_type=None, attr=None, required=True):
        """Attribute constructor.

        :param attr_type: Type, Schema or constant that does the type conversion of the attribute.
        :param attr: Attribute name, dot-separated attribute path or an `Accessor` instance.
        :param required: Is attribute required to be present.
        """
        self.attr_type = attr_type or types.Type
        self.attr = attr
        self.required = required

    @property
    def compartment(self):
        """The key of the compartment this attribute will be placed into (for example: _links or _embedded)."""
        return None

    @property
    def key(self):
        """The key of the this attribute will be placed into (within it's compartment)."""
        return self.name

    @property
    def accessor(self):
        """Get an attribute's accessor with the getter and the setter.

        :return: `Accessor` instance.
        """
        attr = self.attr or self.name

        if isinstance(attr, Accessor):
            return attr

        return Accessor(getter=attr, setter=attr)

    def serialize(self, value):
        """Serialize the attribute of the input data.

        Gets the attribute value with accessor and converts it using the
        type serialization. Schema will place this serialized value into
        corresponding compartment of the HAL structure with the name of the
        attribute as a key.

        :param value: Value to get the attribute value from.
        :return: Serialized attribute value.
        """
        if types.Type.is_type(self.attr_type):
            return self.attr_type.serialize(self.accessor.get(value))
        return self.attr_type

    def deserialize(self, value):
        """Deserialize the attribute from a HAL structure.

        Get the value from the HAL structure from the attribute's compartment
        using the attribute's name as a key, convert it using the attribute's
        type. Schema will either return it to the parent schema or will assign
        to the output value if specified using the attribute's accessor setter.

        :param value: HAL structure to get the value from.
        :return: Deserialized attribute value.
        :raises: ValidationError.
        """
        compartment = value
        if self.compartment is not None:
            compartment = value[self.compartment]
        if self.name in compartment:
            return self.attr_type.deserialize(compartment[self.key])
        elif self.required:
            raise exceptions.ValidationError("Missing attribute.", self.key)

    def __repr__(self):
        """Attribute representation."""
        return "<{0} '{1}'>".format(
            self.__class__.__name__,
            self.name,
        )


class Link(Attr):

    """Link attribute of a schema."""

    def __init__(self, attr_type=None, attr=None, required=True, curie=None, templated=None, type=None):
        """Link constructor.

        :param attr_type: Type, Schema or constant that does the type conversion of the attribute.
        :param attr: Attribute name, dot-separated attribute path or an `Accessor` instance.
        :param required: Is this link required to be present.
        :param curie: Link namespace prefix (e.g. "<prefix>:<name>") or Curie object.
        :param templated: Is this link templated.
        :param type: Its value is a string used as a hint to indicate the media type expected when dereferencing
                           the target resource.
        """
        if not types.Type.is_type(attr_type):

            if attr_type is not None:
                attr = BYPASS

            attrs = {
                'templated': templated,
                'type': type,
            }

            class LinkSchema(Schema):
                href = Attr(attr_type=attr_type, attr=BYPASS)

                if attrs['templated'] is not None:
                    templated = Attr(attr=lambda value: templated)

                if attrs['type'] is not None:
                    type = Attr(attr=lambda value: type)

            attr_type = LinkSchema

        super(Link, self).__init__(attr_type=attr_type, attr=attr, required=required)
        self.curie = curie

    @property
    def compartment(self):
        """Links are placed in the _links."""
        return "_links"

    @property
    def key(self):
        """Links support curies."""
        if self.curie is None:
            return self.name
        return ":".join((self.curie.name, self.name))

    def deserialize(self, value):
        """Links don't support deserialization."""
        raise NotImplementedError


class LinkList(Link):

    """List of links attribute of a schema."""

    def __init__(self, attr_type=None, attr=None, required=True, curie=None):
        """LinkList constructor.

        :param attr_type: Type, Schema or constant that does item type conversion of the attribute.
        :param attr: Attribute name, dot-separated attribute path or an `Accessor` instance.
        :param required: Is this list of links required to be present.
        :param curie: Link namespace prefix (e.g. "<prefix>:<name>") or Curie object.
        """
        super(LinkList, self).__init__(attr_type=attr_type, attr=attr, required=required, curie=curie)
        self.attr_type = types.List(self.attr_type)


class Curie(object):

    """Curie object."""

    def __init__(self, name, href, templated=None, type=None):
        """Curie constructor.

        :param href: Curie link href value.
        :param templated: Is this curie link templated.
        :param type: Its value is a string used as a hint to indicate the media type expected when dereferencing
                           the target resource.
        """
        self.name = name
        self.href = href

        if templated is not None:
            self.templated = templated

        if type is not None:
            self.type = type


class Embedded(Attr):

    """Embedded attribute of schema."""

    def __init__(self, attr_type=None, attr=None, curie=None):
        super(Embedded, self).__init__(attr_type, attr)
        self.curie = curie

    @property
    def compartment(self):
        """Embedded objects are placed in the _objects."""
        return "_embedded"

    @property
    def key(self):
        """Embedded supports curies."""
        if self.curie is None:
            return self.name
        return ":".join((self.curie.name, self.name))

    def serialize(self, value):
        return super(Embedded, self).serialize(value)


class _Schema(types.Type):

    """Type for creating schema."""

    def __new__(cls, **kwargs):
        """Create schema from keyword arguments."""
        schema = type("Schema", (cls, ), {"__doc__": cls.__doc__})
        schema.__class_attrs__ = []
        schema.__attrs__ = []
        for name, attr in kwargs.items():
            if not hasattr(attr, "name"):
                attr.name = name
            schema.__class_attrs__.append(attr)
            schema.__attrs__.append(attr)
        return schema

    @classmethod
    def serialize(cls, value):
        result = {}
        for attr in cls.__attrs__:
            compartment = result
            if attr.compartment is not None:
                compartment = result.setdefault(attr.compartment, {})
            try:
                compartment[attr.key] = attr.serialize(value)
            except (AttributeError, KeyError):
                if attr.required:
                    raise

        return result

    @classmethod
    def deserialize(cls, value, output=None):
        """Deserialize the HAL structure into the output value.

        :param value: Dict of already loaded json which will be deserialized by schema attributes.
        :param output: If present, the output object will be updated instead of returning the deserialized data.

        :returns: Dict of deserialized value for attributes. Where key is name of schema's attribute and value is
        deserialized value from value dict.
        """
        errors = []
        result = {}
        for attr in cls.__attrs__:
            try:
                result[attr.name] = attr.deserialize(value)
            except NotImplementedError:
                # Links don't support deserialization
                continue
            except exceptions.ValidationError as e:
                e.attr = attr.name
                errors.append(e)

        if errors:
            raise exceptions.ValidationError(errors)

        if output is None:
            return result
        for attr in cls.__attrs__:
            attr.accessor.set(output, result[attr.name])


class _SchemaType(type):
    def __init__(cls, name, bases, clsattrs):
        cls.__class_attrs__ = []
        curies = set([])

        # Collect the attributes and set their names.
        for name, value in clsattrs.items():
            if isinstance(value, Attr):

                delattr(cls, name)
                cls.__class_attrs__.append(value)
                if not hasattr(value, "name"):
                    value.name = name

                if isinstance(value, (Link, Embedded)):
                    curie = getattr(value, "curie", None)
                    if curie is not None:
                        curies.add(curie)

        # Collect CURIEs and create the link attribute

        if curies:
            link = LinkList(
                Schema(
                    href=Attr(),
                    name=Attr(),
                    templated=Attr(required=False),
                    type=Attr(required=False),
                ),
                attr=lambda value: list(curies),
                required=False,
            )
            link.name = "curies"

            cls.__class_attrs__.append(link)

        cls.__attrs__ = []
        for base in reversed(cls.__mro__):
            cls.__attrs__.extend(getattr(base, "__class_attrs__", []))


Schema = _SchemaType("Schema", (_Schema, ), {"__doc__": _Schema.__doc__})
