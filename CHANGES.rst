Changelog
=========

2.1.0
-----

* Added Embedded validation


2.0.0
-----

* Added Enum type
* Added OneOfValidator
* **Breaking change**: All types are now non-nullable instead of possibly returning a default or accepting `None`, you should adapt your code accordingly by using `Nullable()`
* Dropped support Python 2


1.7.0
-----

* Fix `List` type raising unrelated errors (or no error at all, when passing a dictionary) when deserializing objects that are not lists.


1.6.1
-----

* Hotfix for 1.6.0: Fix serialization/deserialization error `Schema.serialize(...)` is invoked with kwargs and there are attributes using callables that don't require those kwargs.


1.6.0
-----

* Fix DeprecationWarnings being raised (youtux)
* Dropped support for python 2.6 and add declare support for python 3.5, 3.6, 3.7, 3.8


1.5.0
-----

* Allow passing context keyword arguments to deserialize methods (blaise-io)


1.4.1
-----

* Fix the package setup (olegpidsadnyi)


1.4.0
-----

* Support for vnd.error responses (olegpidsadnyi)


1.3.5
-----

* Add ISO Date Time type (moisesribeiro)


1.3.4
-----

* Nullable type (olegpidsadnyi)


1.3.3
-----

* Strict validation of the ISO8601 (olegpidsadnyi)

1.3.2
-----

* Improve serialization performance (youtux)


1.3.1
-----

* Fix for the String.deserialize to force the text type (olegpidsadnyi)


1.3.0
-----

* Attribute as a decorator (olegpidsadnyi)


1.2.1
-----

* Use native datetime.isoformat for datetime serialization (bubenkoff)

1.1.3
-----

* Correctly handle schema class derivation (bubenkoff)

1.1.2
-----

* Correct deserialization for String and Int types (bubenkoff)

1.1.1
-----

* Deprecation attribute is added to Link (olegpidsadnyi)

1.1.0
-----

* Add common-use types (bubenkoff)

1.0.8
-----

* Correctly handle and document ``required`` and ``default`` (bubenkoff)
* Properly get validator's comparison values (lazy and constant) (bubenkoff)
* Increase test coverage (bubenkoff)

1.0.6
-----

* Respect ValueError in deserialization of the attributes (bubenkoff)

1.0.4
-----

* Correctly render and document deserialization errors (bubenkoff)

1.0.3
-----

* Allow Embedded fields to be marked as not required (mattupstate)
* Field order is preserved in serialized documents (mattupstate)

1.0.0
-----

* Initial public release
