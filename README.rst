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

.. code-block:: python

    import halogen

    spell = {
        "uid": "abracadabra",
        "name": "Abra Cadabra",
        "cost": 10,
    }

    class Spell(halogen.Schema):

        self = halogen.Link(URI("spells"), attr="uid")
        name = halogen.Attr()

    serialized = Spell.serialize(spell)


This will produce HAL-like dictionary which can be serialized to json for the hal+json content type
or to XML for the hal+xml content type.

.. code-block:: json

    {
        "_links": {
            "self": {"href": "spells/abracadabra"}
        },
        "name": "Abra Cadabra"
        // The extra wasn't in the schema and this way will be ignored
    }


Embedded objects
~~~~~~~~~~~~~~~~

.. code-block:: python

    import halogen

    books = [
        {
            "id": "1",
            "name": "Game of Thrones",
        },
        {
            "id": "2",
            "name": "Harry Potter",
        }
    ]

    class Book(halogen.Schema):

        self = halogen.Link(URI("books"), attr="id")
        name = halogen.Attr()

    class BooksFeed(halogen.Schema):
        self = halogen.Link(URI("books"), attr=lambda value: "/")
        books = halogen.Embedded(halogen.types.List(Book))

    feed = Spell.serialize(books)


The serialized data will look like this:

.. code-block:: json

    {
        "_links": {
            "self": {"href": "/books/"}
        },
        "_embedded": {
            "books": [
                {
                    "_links": {
                        "self": {"href": "/books/1"}
                    },
                    "name": "Game of Thrones"

                },
                {
                    "_links": {
                        "self": {"href": "/books/2"}
                    },
                    "name": "Harry Potter"
                }
            ]
        }
    }



Deserialization
---------------

The HAL data can be deserialized into the output object. In case there are validation errors
they will be collected and the ValidationError thrown.


.. code-block:: python

    import halogen

    hal = {
        "_links": {
            "self": {"href": "spells/abracadabra"}
        },
        "name": "Abra Cadabra",
    }

    class Spell(halogen.Schema):

        self = halogen.Link(URI("spells"), attr="uid")
        name = halogen.Attr()

    spell = {}
    Spell.deserialize(hal, output=spell)


The deserialized data will look like this:

.. code-block:: python

    {
        "uid": "abracadabra",
        "name": "Abra Cadabra",
    }

Error handling
--------------

The errors will be related to the attributes.

.. code-block:: python

    try:
        Spell.deserialize(hal, output=spell)
    except halogen.ValidationError as e;
        print e.as_dict()
