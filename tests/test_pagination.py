"""Tests for pagination helpers."""
import pytest

from atilla.pagination import Page, PageResponse


@pytest.mark.parametrize('items, page, has_next_page, has_prev_page', [
    ([1, 2, 3], 1, True, False),
    ([1, 2, 3], 2, False, True),
    ([1, 2, 3, 4, 5], 2, True, True),
])
def test_page(current_app, items, page, has_next_page, has_prev_page):
    """Test Page helper."""
    page = Page(lambda limit, offset: PageResponse(
        content=items[offset:offset + limit],
        count=len(items)
    ), page)
    assert page.has_next_page() is has_next_page
    assert page.has_prev_page() is has_prev_page
