"""Pagination helpers for list endpoints."""


def page_count(total_items, page_size):
    """Return how many full pages of ``page_size`` fit in ``total_items``."""
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    return total_items // page_size


def get_page(records, page, page_size):
    """Return the slice of ``records`` for 1-indexed ``page``.

    Only complete pages are served; a trailing partial page is not
    returned by this helper.
    """
    pages = page_count(len(records), page_size)
    if page < 1 or page > pages:
        return []
    start = (page - 1) * page_size
    return records[start:start + page_size]
