"""Warehouse inventory helpers."""


def list_low_stock(items, threshold):
    """Return items whose quantity is below ``threshold``.

    Each item is a dict with at least ``sku`` and ``quantity`` keys.
    """
    by_sku = {it["sku"]: it for it in items if it["quantity"] < threshold}
    return list(by_sku.values())


def total_units(items):
    """Return the total number of units across all items."""
    return sum(it["quantity"] for it in items)
