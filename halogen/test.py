from halogen import Attr, Schema
from halogen.types import Int, List, Nullable


class PaginationResponse(Schema):
    """Pagination details."""

    total = Attr(Int())
    test = Attr(Nullable(Int()))
    x = Attr(List(Int()))
