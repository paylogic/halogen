from __future__ import annotations
from typing import TypedDict, Optional, NotRequired, Required
import halogen

class PaginationResponseSerialized(TypedDict, total=True):
    total: int
    test: typing.Union[int, None]
    x: list[int]

class PaginationResponse(halogen.Schema):
    @classmethod
    def serialize(cls, value, **kwargs) -> PaginationResponseSerialized: ...
    @classmethod
    def deserialize(cls, value, output=None, **kwargs) -> dict: ...
