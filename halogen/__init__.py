"""halogen public API."""

__version__ = '1.1.3'

try:
    from halogen.schema import Schema, Attr, Link, Curie, Embedded, Accessor
    from halogen import types
    from halogen import validators
    from halogen import exceptions

    __all__ = [
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
