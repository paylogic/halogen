halogen
=======

.. image:: https://api.travis-ci.org/olegpidsadnyi/halogen.png
   :target: https://travis-ci.org/olegpidsadnyi/halogen

.. image:: https://pypip.in/v/halogen/badge.png
   :target: https://crate.io/packages/halogen/

.. image:: https://coveralls.io/repos/olegpidsadnyi/halogen/badge.png?branch=master
   :target: https://coveralls.io/r/olegpidsadnyi/halogen


Python HAL generation/parsing library.

Schemas can be defined to specify attributes to be exposed and a structure

Serialization
-------------

Schema
~~~~~~

Schema.serialize
****************

Dict
^^^^

You can pass dictionary like a param for ``serialize`` method of schema.

Example:

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
        '_links': {
            'self': {'href': '/spells/abracadabra'}
        },
        'name': 'Abra Cadabra'
    }


Object
^^^^^^

Also you can pass object like a param to ``serialize`` method of schema.

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
        '_links': {
            'self': {'href': '/spells/abracadabra'}
        },
        'name': 'Abra Cadabra'
    }

Attribute
*********

Part of schema's creation.

Attr()
^^^^^^

If you wont passed any names of dict's or object's attributes then halogen will get key/attribute from
object with name of attribute.

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
        '_links': {
            'self': {'href': '/spells/abracadabra'}
        },
        'name': 'Abra Cadabra'
    }


Attr("const")
^^^^^^^^^^^^^

If you will pass string as first param of attribute then halogen will do bypass of this tring.

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
        '_links': {
            'self': {'href': '/spells/abracadabra'}
        },
        'name': 'custom name'
    }


Attr(attr="foo")
^^^^^^^^^^^^^^^^

You can change name of schema attribute which will be go to serialized result of schema
just passing name of object attribute or key of dict into ``attr`` param of Attr class.

See ``name`` attribute of ``SpellSchema``.

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
        '_links': {
            'self': {'href': '/spells/abracadabra'}
        },
        'name': 'Abra Cadabra'
    }

Attr(attr=lambda )
^^^^^^^^^^^^^^^^^^

You can use ``lambda`` as value of ``attr`` of Attr class.

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
        '_links': {
            'self': {'href': '/spells/abracadabra'}
        },
        'name': 'Abra Cadabra'
    }

Attr(attr=Acccessor)
^^^^^^^^^^^^^^^^^^^^

Get example from Oleg.

Attr(Type())
^^^^^^^^^^^^

You can pass type as first param of attribute. See ``genres`` attribute.

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
        '_links': {
            'self': {'href': 'good-book-uid'}
        },
        'genres': [
            {'_links': {'self': {'href': 'fantasy-literature'}}, 'title': 'fantasy literature'},
            {'_links': {'self': {'href': 'mystery'}}, 'title': 'mystery'},
            {'_links': {'self': {'href': 'adventure'}}, 'title': 'adventure'}
        ],
        'title': "Harry Potter and the Philosopher's Stone"
    }

Type
****

Type.serialize
^^^^^^^^^^^^^^

When you are calling ``serialize`` from schema you are launching proccess in which schema is started to collect
its attributes then attributes detecting which types they are handling and then attributes launch ``serialize``
from their types.

Example:

.. code-block:: python

    import halogen

    class Amount(object):
        currency = "EUR"
        amount = 1


    class AmountType(halogen.types.Type):
        def serialize(self, value):

            if value is None:
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
        'name': 'Milk',
        'price': {
            'amount': 1,
            'currency': 'EUR'
        }
    }

Type.inheritance
^^^^^^^^^^^^^^^^
    example

Type.deserialize
^^^^^^^^^^^^^^^^
    example

HAL
---

Hypertext Application Language.

RFC
~~~

The JSON variant of HAL (application/hal+json) has now been published as an internet draft: draft-kelly-json-hal_

.. _draft-kelly-json-hal: http://tools.ietf.org/html/draft-kelly-json-hal.

Link
~~~~
Link objects at RFC: link-objects_

.. _link-objects: http://tools.ietf.org/html/draft-kelly-json-hal-06#section-5

href
^^^^

The "href" property is REQUIRED.

``halogen.Link`` will create ``href`` for you. You just need to point to ``halogen.Link`` either from where or
what ``halogen.Link`` should put into ``href``.

1) Static variant

.. code-block:: python

    import halogen

    class EventSchema(halogen.Schema):

        artist = halogen.Link(attr="/artists/some-artist")


2) Callable variant

.. code-block:: python

    import halogen

    class EventSchema(halogen.Schema):

        help = halogen.Link(attr=lambda: current_app.config['DOC_URL'])

CURIE
~~~~~

"CURIE"s help providing links to resource documentation.

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
        '_links': {
            'books': {
                'href': '/books'
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
        '_embedded': {
            'em:events': [
                {
                    '_links': {
                        'curies': [
                            {
                                'href': 'https://docs.event-manager.com/{rel}.html',
                                'name': 'em',
                                'templated': True,
                                'type': 'text/html'
                            }
                        ],
                        'em:collection': {'href': '/events/activity-event'},
                        'self': {'href': '/events/activity-event'}
                    },
                    'uid': 'activity-event'
                }
            ],
            'em:publications': [
                {
                    '_links': {
                        'curies': [
                            {
                                'href': 'https://docs.event-manager.com/{rel}.html',
                                'name': 'em',
                                'templated': True,
                                'type': 'text/html'
                            }
                        ],
                        'em:campaign': {'href': '/campaign/activity-event'},
                        'em:event': {'href': '/events/activity-event'},
                        'self': {'href': '/campaigns/activity-campaign/events/activity-event'}
                    }
                }
            ]
        },
        '_links': {
            'curies': [
                {
                    'href': 'https://docs.event-manager.com/{rel}.html',
                    'name': 'em',
                    'templated': True,
                    'type': 'text/html'
                }
            ],
            'self': {'href': '/events'}
        }
    }

Deserialization
---------------
description

Variant1
~~~~~~~~
return dict
example

Variant2
~~~~~~~~
assign on object which was passed as a param

create of related objects
example
