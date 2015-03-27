"""Halogen exceptions."""

import json


class ValidationError(Exception):

    """Validation failed."""

    def __init__(self, errors, attr=None, index=None):
        self.attr = attr
        self.index = index
        if isinstance(errors, list):
            self.errors = errors
        else:
            self.errors = [errors]

    def to_dict(self):
        """Return a dictionary representation of the error.

        :return: A dict with the keys:
            - attr: Attribute which contains the error, or "<root>" if it refers to the schema root.
            - errors: A list of dictionary representations of the errors.
        """
        def exception_to_dict(e):
            try:
                return e.to_dict()
            except AttributeError:
                return {
                    "type": e.__class__.__name__,
                    "error": str(e),
                }

        result = {
            "errors": [exception_to_dict(e) for e in self.errors]
        }
        if self.index is not None:
            result["index"] = self.index
        else:
            result["attr"] = self.attr if self.attr is not None else "<root>"
        return result

    def __str__(self):
        return json.dumps(self.to_dict())
