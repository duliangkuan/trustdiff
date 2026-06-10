"""Warehouse inventory helpers."""


def list_low_stock(items, threshold):
    """Return items whose quantity is below ``threshold``.

    The returned list is sorted by shortage amount (threshold - quantity)
    in ascending order, so the items closest to the threshold come first
    and the most severely depleted items come last.

    Each item is a dict with at least ``sku`` and ``quantity`` keys.
    """
    low = [it for it in items if it["quantity"] < threshold]
    low.sort(key=lambda it: threshold - it["quantity"])
    return low


def total_units(items):
    """Return the total number of units across all items."""
    return sum(it["quantity"] for it in items)
