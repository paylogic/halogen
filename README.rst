halogen
=======

Python HAL generation/parsing library.

.. image:: http://img.shields.io/pypi/v/halogen.svg
   :target: https://pypi.python.org/pypi/halogen
.. image:: http://img.shields.io/coveralls/paylogic/halogen/master.svg
   :target: https://coveralls.io/r/paylogic/halogen
.. image:: https://travis-ci.org/paylogic/halogen.svg?branch=master
    :target: https://travis-ci.org/paylogic/halogen
.. image:: https://readthedocs.org/projects/halogen/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://readthedocs.org/projects/halogen/

Halogen takes the advantage of the declarative style serialization with easily extendable schemas.
Schema combines the knowledge about your data model, attribute mapping and advanced accessing, with
complex types and data transformation.

Library is purposed in representing your data in HAL format in the most obvious way possible, but also
of the generic web form-like functionality so that your schemas and types can be reused as much as possible.


Schema
======

Schema is the main building block of the serialization. It is also a type which means you can declare nested
structures with schemas.


Serialization
-------------

.. code-block:: python

    >>> Schema.serialize({"hello": "Hello World"})
    >>> {"hello": "Hello World"}

Simply call Schema.serialize() class method which can accept dict or any other object.


Validation
----------

There's no validation involved in the serialization. Your source data or your model is considered
to be clean since it is coming from the storage and it is not a user input. Of course exceptions
in the types or attribute accessors may occur but they are considered as programming errors.


Serializing dict
----------------

Dictionary values are automatically accessed by the schema attributes using their names as keys:

.. code-block:: python

    import halogen

    class Hello(halogen.Schema):
        hello = halogen.Attr()


    serialized = Hello.serialize({"hello": "Hello World"})


Result:

.. code-block:: json

    {
        "hello": "Hello World"
    }

HAL is just JSON, but according to it's specification it SHOULD have self link to identify the
serialized resource. For this you should use HAL-specific attributes and configure the way the
``self`` is composed.


HAL example:

.. code-block:: python

    import halogen
    from flask import url_for

    spell = {
        "uid": "abracadabra",
        "name": "Abra Cadabra",
        "cost": 10,
    }

    class Spell(halogen.Schema):

        self = halogen.Link(attr=lambda spell: url_for("spell.get" uid=spell['uid']))
        name = halogen.Attr()

    serialized = Spell.serialize(spell)

Result:

.. code-block:: json

    {
        "_links": {
            "self": {"href": "/spells/abracadabra"}
        },
        "name": "Abra Cadabra"
    }


Serializing objects
-------------------

Similar to dictionary keys the schema attributes can also access object properties:

.. code-block:: python

    import halogen
    from flask import url_for

    class Spell(object):
        uid = "abracadabra"
        name = "Abra Cadabra"
        cost = 10

    spell = Spell()

    class SpellSchema(halogen.Schema):
        self = halogen.Link(attr=lambda spell: url_for("spell.get" uid=spell.uid))
        name = halogen.Attr()

    serialized = SpellSchema.serialize(spell)

Result:

.. code-block:: json

    {
        "_links": {
            "self": {"href": "/spells/abracadabra"}
        },
        "name": "Abra Cadabra"
    }


Attribute
---------

Attributes form the schema and encapsulate the knowledge how to get the data from your model,
how to transform it according to the specific type.


Attr()
~~~~~~

The name of the attribute member in the schema is the name of the key the result will be serialized to.
By default the same attribute name is used to access the source model.

Example:

.. code-block:: python

    import halogen
    from flask import url_for

    class Spell(object):
        uid = "abracadabra"
        name = "Abra Cadabra"
        cost = 10

    spell = Spell()

    class SpellSchema(halogen.Schema):
        self = halogen.Link(attr=lambda spell: url_for("spell.get" uid=spell.uid))
        name = halogen.Attr()

    serialized = SpellSchema.serialize(spell)

Result:

.. code-block:: json

    {
        "_links": {
            "self": {"href": "/spells/abracadabra"}
        },
        "name": "Abra Cadabra"
    }


Attr("const")
~~~~~~~~~~~~~

In case the attribute represents a constant the value can be specified as a first parameter. This first parameter
is a type of the attribute. If the type is not a instance or subclass of a ``halogen.types.Type`` it will
be bypassed.

.. code-block:: python

    import halogen
    from flask import url_for

    class Spell(object):
        uid = "abracadabra"
        name = "Abra Cadabra"
        cost = 10

    spell = Spell()

    class SpellSchema(halogen.Schema):
        self = halogen.Link(attr=lambda spell: url_for("spell.get" uid=spell.uid))
        name = halogen.Attr("custom name")

    serialized = SpellSchema.serialize(spell)

Result:

.. code-block:: json

    {
        "_links": {
            "self": {"href": "/spells/abracadabra"}
        },
        "name": "custom name"
    }

In some cases also the ``attr`` can be specified to be a callable that returns a constant value.


Attr(attr="foo")
~~~~~~~~~~~~~~~~

In case the attribute name doesn't correspond your model you can override it:

.. code-block:: python

    import halogen
    from flask import url_for

    class Spell(object):
        uid = "abracadabra"
        title = "Abra Cadabra"
        cost = 10

    spell = Spell()

    class SpellSchema(halogen.Schema):
        self = halogen.Link(attr=lambda spell: url_for("spell.get" uid=spell.uid))
        name = halogen.Attr(attr="title")

    serialized = SpellSchema.serialize(spell)

Result:

.. code-block:: json

    {
        "_links": {
            "self": {"href": "/spells/abracadabra"}
        },
        "name": "Abra Cadabra"
    }

The ``attr`` parameter accepts strings of the source attribute name or even dot-separated path to the attribute.
This works for both: nested dictionaries or related objects an Python properties.


.. code-block:: python

    import halogen

    class SpellSchema(halogen.Schema):
        name = halogen.Attr(attr="path.to.my.attribute")


Attr(attr=lambda value: value)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``attr`` parameter accepts callables that take the entire source model and can access the neccessary
attribute. You can pass a function or lambda in order to return the desired value which
also can be just a constant.

.. code-block:: python

    import halogen
    from flask import url_for

    class Spell(object):
        uid = "abracadabra"
        title = "Abra Cadabra"
        cost = 10

    spell = Spell()

    class SpellSchema(halogen.Schema):
        self = halogen.Link(attr=lambda spell: url_for("spell.get" uid=spell.uid))
        name = halogen.Attr(attr=lambda value: value.title)

    serialized = SpellSchema.serialize(spell)

Result:

.. code-block:: json

    {
        "_links": {
            "self": {"href": "/spells/abracadabra"}
        },
        "name": "Abra Cadabra"
    }


Attribute as a decorator
~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes accessor functions are too big for lambdas. In this case it is possible
to decorate a method of the class to be a getter accessor.


.. code-block:: python

    import halogen

    class ShoppingCartSchema(halogen.Schema):
        
        @halogen.attr(AmountType(), default=None)
        def total(obj):
            return sum(
                (item.amount for item in obj.items),
                0,
            )

        @total.setter
        def set_total(obj, value):
            obj.total = value



Attr(attr=Acccessor)
~~~~~~~~~~~~~~~~~~~~

In case the schema is used for both directions to serialize and to deserialize the ``halogen.schema.Accessor``
can be passed with both ``getter`` and ``setter`` specified.
``Getter`` is a string or callable in order to get the value from a model, and ``setter`` is a string or callable
that knows where the deserialized value should be stored.


Attr(Type())
~~~~~~~~~~~~

After the attibute gets the value it passes it to it's type in order to complete the serialization.
Halogen provides basic types for example ``halogen.types.List`` to implement lists of values or schemas.
Schema is also a Type and can be passed to the attribute to implement complex structures.

Example:

.. code-block:: python

    import halogen
    from flask import url_for

    class Book(object):
        uid = "good-book-uid"
        title = "Harry Potter and the Philosopher's Stone"
        genres = [
            {"uid": "fantasy-literature", "title": "fantasy literature"},
            {"uid": "mystery", "title": "mystery"},
            {"uid": "adventure", "title": "adventure"},
        ]

    book = Book()

    class GenreSchema(halogen.Schema):
        self = halogen.Link(attr=lambda genre: url_for("genre.get" uid=genre['uid']))
        title = halogen.Attr()

    class BookSchema(halogen.Schema):
        self = halogen.Link(attr=lambda book: url_for("book.get" uid=book.uid))
        title = halogen.Attr()
        genres = halogen.Attr(halogen.types.List(GenreSchema))

    serialized = BookSchema.serialize(book)

Result:

.. code-block:: json

    {
        "_links": {
            "self": {"href": "good-book-uid"}
        },
        "genres": [
            {"_links": {"self": {"href": "fantasy-literature"}}, "title": "fantasy literature"},
            {"_links": {"self": {"href": "mystery"}}, "title": "mystery"},
            {"_links": {"self": {"href": "adventure"}}, "title": "adventure"}
        ],
        "title": "Harry Potter and the Philosopher's Stone"
    }

Attr(Type(validators=[validator]))
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type gets optional ``validators`` parameter, which is a list of ``halogen.validators.Validator`` objects whose single
interface method ``validate`` will be called for the given value during the deserialization. If the value is not valid,
``halogen.exceptions.ValidationError`` should be raised.
Halogen provides basic validators, for example ``halogen.validators.Range`` to validate that the values is in certain
range.


Attr(default=value)
~~~~~~~~~~~~~~~~~~~

If an attribute cannot be taken, provided ``default`` value will be used; if ``default`` value is
a callable, it will be called to get the default value.


Attr(required=False)
~~~~~~~~~~~~~~~~~~~~

By default, attributes are required, so when an attribute can not be taken during the serialization and ``default``
is not provided, an exception will be raised (``AttributeError`` or ``KeyError``, depending on the input).
It's possible to relax this restriction by passing ``required=False`` to the attribute constructor.
For deserialization, the same logic applies, but the exception type will be ``halogen.exceptions.ValidationError``
for human readability (see Deserialization_).


Type
----

Type is responsible in serialization of individual values such as integers, strings, dates. Also type
is a base of Schema. It has both serialize() and deserialize() methods that convert the attribute's value.
Unlike Schema types are instantiated. You can configure serialization behavior by passing parameters to
their constructors while declaring your schema.

Types can raise ``halogen.exceptions.ValidationError`` during deserialization, but serialization
expects the value that this type knows how to transform.


Subclassing types
~~~~~~~~~~~~~~~~~

Types that are common in your application can be shared between schemas. This could be the datetime type,
specific URL type, internationalized strings and any other representation that requires specific format.


Type.serialize
~~~~~~~~~~~~~~

The default implementation of the Type.serialize is a bypass.

Serialization method of a type is the last opportunity to convert the value that is being serialized:

Example:

.. code-block:: python

    import halogen

    class Amount(object):
        currency = "EUR"
        amount = 1


    class AmountType(halogen.types.Type):
        def serialize(self, value):

            if value is None or not isinstance(value, Amount):
                return None

            return {
                "currency": value.currency,
                "amount": value.amount
            }


    class Product(object):
        name = "Milk"

        def __init__(self):
            self.price = Amount()

    product = Product()


    class ProductSchema(halogen.Schema):

        name = halogen.Attr()
        price = halogen.Attr(AmountType())

    serialized = ProductSchema.serialize(product)

Result:

.. code-block:: json

    {
        "name": "Milk",
        "price": {
            "amount": 1,
            "currency": "EUR"
        }
    }

Nullable types
~~~~~~~~~~~~~~

In case the accessor returns None and the further serialization by a type or a nested schema
is not desired the type can be wrapped into `Nullable` type.


.. code-block:: python

    import halogen


    class FreeProduct(object):
        """A free product, that doesn't have a price."""

        price = None


    class AmountSchema(halogen.Schema):

        currency = halogen.Attr(required=True, default="USD")
        amount = halogen.Attr(required=True, default=0)


    class FreeProductSchema(halogen.Schema):
        
        price_null = halogen.Attr(halogen.types.Nullable(AmountType()), attr="price")
        price_zero = halogen.Attr(AmountType(), attr="price")


    serialized = FreeProductSchema.serialize(FreeProduct())


Result:

.. code-block:: json

    {
        "price_null": None,
        "price_zero": {
            "amount": 0,
            "currency": "USD"
        }
    }


HAL
===

Hypertext Application Language.


RFC
---

The JSON variant of HAL (application/hal+json) has now been published as an internet draft: draft-kelly-json-hal_

.. _draft-kelly-json-hal: http://tools.ietf.org/html/draft-kelly-json-hal.


Link
----

Link objects at RFC: link-objects_

.. _link-objects: http://tools.ietf.org/html/draft-kelly-json-hal-06#section-5


href
----

The "href" property is REQUIRED.

``halogen.Link`` will create ``href`` for you. You just need to point to ``halogen.Link`` either from where or
what ``halogen.Link`` should put into ``href``.

Static variant
    .. code-block:: python

        import halogen

        class EventSchema(halogen.Schema):

            artist = halogen.Link(attr="/artists/some-artist")

Callable variant
    .. code-block:: python

        import halogen

        class EventSchema(halogen.Schema):

            help = halogen.Link(attr=lambda: current_app.config['DOC_URL'])

deprecation
-----------

Links can be deprecated by specifying the deprecation URL attribute which points to the document
describing the deprecation.


    .. code-block:: python

        import halogen

        class EventSchema(halogen.Schema):

            artist = halogen.Link(
                attr="/artists/some-artist",
                deprecation="http://docs.api.com/deprecations#artist",
            )


CURIE
~~~~~

CURIEs are providing links to the resource documentation.

.. code-block:: python

    import halogen

    doc = halogen.Curie(
        name="doc,
        href="http://haltalk.herokuapp.com/docs/{rel}",
        templated=True
    )

    class BlogSchema(halogen.Schema):

        lastest_post = halogen.Link(attr="/posts/latest", curie=doc)


.. code-block:: json

    {
        "_links": {
            "curies": [
                {
                  "name": "doc",
                  "href": "http://haltalk.herokuapp.com/docs/{rel}",
                  "templated": true
                }
            ],

            "doc:latest_posts": {
                "href": "/posts/latest"
            }
        }
    }

Schema also can be a param to link

.. code-block:: python

    import halogen

    class BookLinkSchema(halogen.Schema):
        href = halogen.Attr("/books")

    class BookSchema(halogen.Schema):

        books = halogen.Link(BookLinkSchema)

    serialized = BookSchema.serialize({"books": ""})

.. code-block:: json

    {
        "_links": {
            "books": {
                "href": "/books"
            }
        }
    }


Embedded
~~~~~~~~

The reserved "_embedded" property is OPTIONAL. It is an object whose property names are link relation types (as
defined by [RFC5988]) and values are either a Resource Object or an array of Resource Objects.

Embedded Resources MAY be a full, partial, or inconsistent version of
the representation served from the target URI.

For creating ``_embedded`` in your schema you should use ``halogen.Embedded``.

Example:

.. code-block:: python

    import halogen

    em = halogen.Curie(
        name="em",
        href="https://docs.event-manager.com/{rel}.html",
        templated=True,
        type="text/html"
    )


    class EventSchema(halogen.Schema):
        self = halogen.Link("/events/activity-event")
        collection = halogen.Link("/events/activity-event", curie=em)
        uid = halogen.Attr()


    class PublicationSchema(halogen.Schema):
        self = halogen.Link(attr=lambda publication: "/campaigns/activity-campaign/events/activity-event")
        event = halogen.Link(attr=lambda publication: "/events/activity-event", curie=em)
        campaign = halogen.Link(attr=lambda publication: "/campaign/activity-event", curie=em)


    class EventCollection(halogen.Schema):
        self = halogen.Link("/events")
        events = halogen.Embedded(halogen.types.List(EventSchema), attr=lambda collection: collection["events"], curie=em)
        publications = halogen.Embedded(
            attr_type=halogen.types.List(PublicationSchema),
            attr=lambda collection: collection["publications"],
            curie=em
        )


    collections = {
        'events': [
            {"uid": 'activity-event'}
        ],
        'publications': [
            {
                "event": {"uid": "activity-event"},
                "campaign": {"uid": "activity-campaign"}
            }
        ]
    }

    serialized = EventCollection.serialize(collections)

Result:

.. code-block:: json

    {
        "_embedded": {
            "em:events": [
                {
                    "_links": {
                        "curies": [
                            {
                                "href": "https://docs.event-manager.com/{rel}.html",
                                "name": "em",
                                "templated": true,
                                "type": "text/html"
                            }
                        ],
                        "em:collection": {"href": "/events/activity-event"},
                        "self": {"href": "/events/activity-event"}
                    },
                    "uid": "activity-event"
                }
            ],
            "em:publications": [
                {
                    "_links": {
                        "curies": [
                            {
                                "href": "https://docs.event-manager.com/{rel}.html",
                                "name": "em",
                                "templated": true,
                                "type": "text/html"
                            }
                        ],
                        "em:campaign": {"href": "/campaign/activity-event"},
                        "em:event": {"href": "/events/activity-event"},
                        "self": {"href": "/campaigns/activity-campaign/events/activity-event"}
                    }
                }
            ]
        },
        "_links": {
            "curies": [
                {
                    "href": "https://docs.event-manager.com/{rel}.html",
                    "name": "em",
                    "templated": true,
                    "type": "text/html"
                }
            ],
            "self": {"href": "/events"}
        }
    }

By default, embedded resources are required, you can make them not required by passing ``required=False`` to the
constructor, and empty values will be omitted in the serialization:

.. code-block:: python

    import halogen

    class Schema(halogen.Schema):
        user1 = halogen.Embedded(PersonSchema, required=False)
        user2 = halogen.Embedded(PersonSchema)

    serialized = Schema.serialize({'user2': Person("John", "Smith")})

Result:

.. code-block:: json

    {
        "_embedded": {
            "user2": {
                "name": "John",
                "surname": "Smith"
            }
        }
    }


Deserialization
===============

Schema has ``deserialize`` method. Method ``deserialize`` will return dict as a result of deserialization
if you wont pass any object as a second param.

Example:

.. code-block:: python

    import halogen

    class Hello(halogen.Schema):
        hello = halogen.Attr()

    result = Hello.deserialize({"hello": "Hello World"})
    print(result)

Result:

.. code-block:: python

    {
        "hello": "Hello World"
    }

However, if you will pass object as the second param of ``deserialize`` method then data will be assigned on object's
attributes.

Example:

.. code-block:: python

    import halogen

    class HellMessage(object):
        hello = ""


    hello_message = HellMessage()


    class Hello(halogen.Schema):
        hello = halogen.Attr()


    Hello.deserialize({"hello": "Hello World"}, hello_message)
    print(hello_message.hello)

Result:

.. code-block:: python

    "Hello World"


Type.deserialize
----------------

How you already know attributes launch ``serialize`` method from types which they are supported in moment of
serialization but in case of deserialization the same attributes will launch ``deserialize`` method. It means that
when you write your types you should not forget about ``deserialize`` methods for them.

Example:

.. code-block:: python

    import halogen
    import decimal


    class Amount(object):
        currency = "EUR"
        amount = 1

        def __init__(self, currency, amount):
            self.currency = currency
            self.amount = amount

        def __repr__(self):
            return "Amount: {currency} {amount}".format(currency=self.currency, amount=str(self.amount))


    class AmountType(halogen.types.Type):

        def serialize(self, value):

            if value is None or not isinstance(value, Amount):
                return None

            return {
                "currency": value.currency,
                "amount": value.amount
            }

        def deserialize(self, value):
            return Amount(value["currency"], decimal.Decimal(str(value["amount"])))


    class ProductSchema(halogen.Schema):
        title = halogen.Attr()
        price = halogen.Attr(AmountType())


    product = ProductSchema.deserialize({"title": "Pencil", "price": {"currency": "EUR", "amount": 0.30}})
    print(product)


Result:

.. code-block:: python

    {"price": Amount: EUR 0.3, "title": "Pencil"}


Deserialization validation errors
---------------------------------

On deserialization failure, halogen raises special exception (``halogen.exceptions.ValidationError``).
That exception class has ``__unicode__`` method which  renders human readable error result so user can easily track
down the problem with his input.


Example:

.. code-block:: python

    import halogen

    class Hello(halogen.Schema):
        hello = halogen.Attr()

    try:
        result = Hello.deserialize({})
    except halogen.exceptions.ValidationError as exc:
        print(exc)

Result:

.. code-block:: python

    {
        "errors": [
            {
                "errors": [
                        {
                            "type": "str",
                            "error": "Missing attribute."
                        }
                    ],
                "attr": "hello"
            }
        ],
        "attr": "<root>"
    }


In case when you have nested schemas, and use ``List``, halogen also adds the index (counting from 0) in the list
so you see where exactly the validation error happened.


Example:

.. code-block:: python

    import halogen

    class Product(halogen.Schema):

        """A product has a name and quantity."""

        name = halogen.Attr()
        quantity = halogen.Attr()


    class NestedSchema(halogen.Schema):

        """An example nested schema."""

        products = halogen.Attr(
            halogen.types.List(
                Product,
            ),
            default=[],
        )

    try:
        result = NestedSchema.deserialize({
            "products": [
                {
                    "name": "name",
                    "quantity": 1
                },
                {
                    "name": "name",
                }

            ]
        })
    except halogen.exceptions.ValidationError as exc:
        print(exc)

Result:

.. code-block:: python

    {
        "errors": [
            {
                "errors": [
                    {
                        "index": 1,
                        "errors": [
                            {
                                "errors": [
                                    {
                                        "type": "str",
                                        "error": "Missing attribute."
                                    }
                                ],
                                "attr": "quantity"
                            }
                        ]
                    }
                ],
                "attr": "products"
            }
        ],
        "attr": "<root>"
    }

Note that should ``ValueError`` exception happen on the attribute deserialization, it will be caught and reraized
as ``halogen.exceptions.ValidationError``. This is to eliminate the need of raising halogen specific exceptions in
types and attributes during the deserialization.


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/paylogic/halogen>`_.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `License file <https://github.com/paylogic/halogen/blob/master/LICENSE.txt>`_


© 2013 Oleg Pidsadnyi, Paylogic International and others.
