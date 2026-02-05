from typing import final
from halogen import Attr, Schema
from halogen.types import Int, List, Nullable


@final
class PaginationResponse(Schema):
    """Pagination details."""

    total = Attr(Int())
    test = Attr(Nullable(Int()))
    x = Attr(List(Int()))
