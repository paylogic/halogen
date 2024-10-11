"""halogen public API."""

__version__ = "2.0.0"

try:
    from halogen.schema import Schema, attr, Attr, Link, Curie, Embedded, Accessor
    from halogen import types
    from halogen import validators
    from halogen import exceptions

    __all__ = [
        "attr",
        "Accessor",
        "Attr",
        "Curie",
        "Embedded",
        "exceptions",
        "Link",
        "Schema",
        "types",
        "validators",
    ]
except ImportError:  # pragma: no cover
    # avoid import errors when only __version__ is needed (for setup.py)
    pass
