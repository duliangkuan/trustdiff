"""Pagination helpers for list endpoints."""

import math


def page_count(total_items, page_size):
    """Return how many pages of ``page_size`` cover ``total_items``.

    A trailing partial page counts as a full page.
    """
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    return math.ceil(total_items / page_size)


def get_page(records, page, page_size):
    """Return the slice of ``records`` for 1-indexed ``page``.

    The final partial page is included.
    """
    pages = page_count(len(records), page_size)
    if page < 1 or page > pages:
        return []
    start = (page - 1) * page_size
    return records[start:start + page_size]
