"""Halogen exceptions."""

import json


class ValidationError(Exception):
    """It will be raised when validation will be failed."""

    def __init__(self, errors, attr=None):
        self.attr = attr
        if isinstance(errors, list):
            self.errors = errors
        else:
            self.errors = [errors]

    def to_dict(self):
        """Return a dictionary representation of the error, with the following keys:
        - attr: Attribute which contains the error, or "<root>" if it refers to the schema root.
        - errors: A list of dictionary representations of the errors.
        """
        def exception_to_dict(e):
            try:
                return e.to_dict()
            except AttributeError:
                return {
                    "type": e.__class__.__name__,
                    "error": str(e)
                }

        return {
            "attr": self.attr if self.attr is not None else "<root>",
            "errors": [exception_to_dict(e) for e in self.errors]
        }

    def __str__(self):
        return json.dumps(self.to_dict())
