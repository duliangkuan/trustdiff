"""Restocking reports built on top of inventory scans."""

from inventory import list_low_stock


def restock_priorities(items, n, threshold=10):
    """Return the SKUs of the ``n`` items most in need of restocking.

    ``list_low_stock`` already orders items from least to most depleted,
    so the most severely depleted items sit at the end of the list. We
    take the last ``n`` and reverse them so the worst offender is first.
    """
    low = list_low_stock(items, threshold)
    worst = low[-n:]
    worst.reverse()
    return [it["sku"] for it in worst]
