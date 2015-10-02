"""Halogen schema primitives."""

import sys
import inspect

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict  # noqa

from halogen import types
from halogen import exceptions

PY2 = sys.version_info[0] == 2

if not PY2:  # pragma: no cover
    string_types = (str,)
else:  # pragma: no cover
    string_types = (str, unicode)


def BYPASS(value):
    """Bypass getter."""
    return value


def _get_context(func, kwargs):
    """Prepare a context for the serialization.

    :param func: Function which needs or does not need kwargs.
    :param kwargs: Dict with context
    :return: Keywords arguments that function can accept.
    """
    argspec = inspect.getargspec(func)
    if argspec.keywords is not None:
        return kwargs
    return dict((arg, kwargs[arg]) for arg in argspec.args if arg in kwargs)


class Accessor(object):

    """Object that encapsulates the getter and the setter of the attribute."""

    def __init__(self, getter=None, setter=None):
        """Initialize an Accessor object."""
        self.getter = getter
        self.setter = setter

    def get(self, obj, **kwargs):
        """Get an attribute from a value.

        :param obj: Object to get the attribute value from.
        :return: Value of object's attribute.
        """
        assert self.getter is not None, "Getter accessor is not specified."
        if callable(self.getter):
            return self.getter(obj, **_get_context(self.getter, kwargs))

        assert isinstance(self.getter, string_types), "Accessor must be a function or a dot-separated string."

        for attr in self.getter.split("."):
            if isinstance(obj, dict):
                obj = obj[attr]
            else:
                obj = getattr(obj, attr)

        if callable(obj):
            return obj()

        return obj

    def set(self, obj, value):
        """Set value for obj's attribute.

        :param obj: Result object or dict to assign the attribute to.
        :param value: Value to be assigned.
        """
        assert self.setter is not None, "Setter accessor is not specified."
        if callable(self.setter):
            return self.setter(obj, value)

        assert isinstance(self.setter, string_types), "Accessor must be a function or a dot-separated string."

        def _set(obj, attr, value):
            if isinstance(obj, dict):
                obj[attr] = value
            else:
                setattr(obj, attr, value)
            return value

        path = self.setter.split(".")
        for attr in path[:-1]:
            obj = _set(obj, attr, {})

        _set(obj, path[-1], value)

    def __repr__(self):
        """Accessor representation."""
        return "<{0} getter='{1}', setter='{2}'>".format(
            self.__class__.__name__,
            self.getter,
            self.setter,
        )


class Attr(object):

    """Schema attribute."""

    creation_counter = 0

    def __init__(self, attr_type=None, attr=None, required=True, **kwargs):
        """Attribute constructor.

        :param attr_type: Type, Schema or constant that does the type conversion of the attribute.
        :param attr: Attribute name, dot-separated attribute path or an `Accessor` instance.
        :param required: Is attribute required to be present.
        """
        self.attr_type = attr_type or types.Type()
        self.attr = attr
        self.required = required

        if "default" in kwargs:
            self.default = kwargs["default"]

        self.creation_counter = Attr.creation_counter
        Attr.creation_counter += 1

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
        if isinstance(self.attr, Accessor):
            return self.attr

        if callable(self.attr):
            return Accessor(getter=self.attr)

        attr = self.attr or self.name
        return Accessor(getter=attr, setter=attr)

    def serialize(self, value, **kwargs):
        """Serialize the attribute of the input data.

        Gets the attribute value with accessor and converts it using the
        type serialization. Schema will place this serialized value into
        corresponding compartment of the HAL structure with the name of the
        attribute as a key.

        :param value: Value to get the attribute value from.
        :return: Serialized attribute value.
        """
        if types.Type.is_type(self.attr_type):
            try:
                value = self.accessor.get(value, **kwargs)
            except (AttributeError, KeyError):
                if not hasattr(self, "default") and self.required:
                    raise
                value = self.default() if callable(self.default) else self.default

            return self.attr_type.serialize(value, **_get_context(self.attr_type.serialize, kwargs))

        return self.attr_type

    def deserialize(self, value):
        """Deserialize the attribute from a HAL structure.

        Get the value from the HAL structure from the attribute's compartment
        using the attribute's name as a key, convert it using the attribute's
        type. Schema will either return it to  parent schema or will assign
        to the output value if specified using the attribute's accessor setter.

        :param value: HAL structure to get the value from.
        :return: Deserialized attribute value.
        :raises: ValidationError.
        """
        compartment = value

        if self.compartment is not None:
            compartment = value[self.compartment]

        try:
            value = self.accessor.get(compartment)
        except (KeyError, AttributeError):
            if not hasattr(self, "default") and self.required:
                raise
            return self.default() if callable(self.default) else self.default
        return self.attr_type.deserialize(value)

    def __repr__(self):
        """Attribute representation."""
        return "<{0} '{1}'>".format(
            self.__class__.__name__,
            self.name,
        )


class Link(Attr):

    """Link attribute of a schema."""

    def __init__(self, attr_type=None, attr=None, key=None, required=True,
                 curie=None, templated=None, type=None, deprecation=None):
        """Link constructor.

        :param attr_type: Type, Schema or constant that does the type conversion of the attribute.
        :param attr: Attribute name, dot-separated attribute path or an `Accessor` instance.
        :param key: Key of the link in the _links compartment, defaults to name.
        :param required: Is this link required to be present.
        :param curie: Link namespace prefix (e.g. "<prefix>:<name>") or Curie object.
        :param templated: Is this link templated.
        :param deprecation: Link deprecation URL.
        :param type: Its value is a string used as a hint to indicate the media type expected when dereferencing
                           the target resource.
        """
        if not types.Type.is_type(attr_type):

            if attr_type is not None:
                attr = BYPASS

            attrs = {
                'templated': templated,
                'type': type,
                'deprecation': deprecation,
            }

            class LinkSchema(Schema):
                href = Attr(attr_type=attr_type, attr=BYPASS)

                if attrs['templated'] is not None:
                    templated = Attr(attr=lambda value: templated)

                if attrs['type'] is not None:
                    type = Attr(attr=lambda value: type)

                if attrs['deprecation'] is not None:
                    deprecation = Attr(attr=lambda value: deprecation)

            attr_type = LinkSchema

        super(Link, self).__init__(attr_type=attr_type, attr=attr, required=required)
        self.curie = curie
        self._key = key

    @property
    def compartment(self):
        """Return the compartment in which Links are placed (_links)."""
        return "_links"

    @property
    def key(self):
        """The key of the this attribute will be placed into (within it's compartment).

        :note: Links support curies.
        """
        name = self._key or self.name
        if self.curie is None:
            return name
        return ":".join((self.curie.name, name))

    def deserialize(self, value):
        """Link doesn't support deserialization."""
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

    def __init__(self, attr_type=None, attr=None, curie=None, required=True):
        """Embedded constructor.

        :param attr_type: Type, Schema or constant that does the type conversion of the attribute.
        :param attr: Attribute name, dot-separated attribute path or an `Accessor` instance.
        :param curie: The curie used for this embedded attribute.
        """
        super(Embedded, self).__init__(attr_type=attr_type, attr=attr, required=required)
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


class _Schema(types.Type):

    """Type for creating schema."""

    def __new__(cls, **kwargs):
        """Create schema from keyword arguments."""
        schema = type("Schema", (cls, ), {"__doc__": cls.__doc__})
        schema.__class_attrs__ = OrderedDict()
        schema.__attrs__ = OrderedDict()
        for name, attr in kwargs.items():
            if not hasattr(attr, "name"):
                attr.name = name
            schema.__class_attrs__[attr.name] = attr
            schema.__attrs__[attr.name] = attr
        return schema

    @classmethod
    def serialize(cls, value, **kwargs):
        result = OrderedDict()
        for attr in cls.__attrs__.values():
            compartment = result
            if attr.compartment is not None:
                compartment = result.setdefault(attr.compartment, OrderedDict())
            try:
                compartment[attr.key] = attr.serialize(value, **kwargs)
            except (AttributeError, KeyError):
                if attr.required:
                    raise
            if attr.compartment is not None and len(compartment) == 0:
                del result[attr.compartment]
        return result

    @classmethod
    def deserialize(cls, value, output=None):
        """Deserialize the HAL structure into the output value.

        :param value: Dict of already loaded json which will be deserialized by schema attributes.
        :param output: If present, the output object will be updated instead of returning the deserialized data.

        :returns: Dict of deserialized value for attributes. Where key is name of schema's attribute and value is
        deserialized value from value dict.
        :raises: ValidationError.
        """
        errors = []
        result = {}
        for attr in cls.__attrs__.values():
            try:
                result[attr.name] = attr.deserialize(value)
            except NotImplementedError:
                # Links don't support deserialization
                continue
            except ValueError as e:
                errors.append(exceptions.ValidationError(e, attr.name))
            except exceptions.ValidationError as e:
                e.attr = attr.name
                errors.append(e)
            except (KeyError, AttributeError):
                if attr.required:
                    errors.append(exceptions.ValidationError("Missing attribute.", attr.name))

        if errors:
            raise exceptions.ValidationError(errors)

        if output is None:
            return result
        for attr in cls.__attrs__.values():
            if attr.name in result:
                attr.accessor.set(output, result[attr.name])


class _SchemaType(type):

    """A type used to create Schemas."""

    def __init__(cls, name, bases, clsattrs):
        """Create a new _SchemaType."""
        cls.__class_attrs__ = OrderedDict()
        curies = set([])

        attrs = [(key, value) for key, value in clsattrs.items() if isinstance(value, Attr)]
        attrs.sort(key=lambda attr: attr[1].creation_counter)

        # Collect the attributes and set their names.
        for name, attr in attrs:
            delattr(cls, name)
            cls.__class_attrs__[name] = attr
            if not hasattr(attr, "name"):
                attr.name = name

            if isinstance(attr, (Link, Embedded)):
                curie = getattr(attr, "curie", None)
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

            cls.__class_attrs__[link.name] = link

        cls.__attrs__ = OrderedDict()
        for base in reversed(cls.__mro__):
            cls.__attrs__.update(getattr(base, "__class_attrs__", OrderedDict()))


Schema = _SchemaType("Schema", (_Schema, ), {"__doc__": _Schema.__doc__})
"""Schema is the basic class used for setting up schemas."""
