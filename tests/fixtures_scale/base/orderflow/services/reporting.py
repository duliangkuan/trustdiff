"""Reporting service: revenue and inventory roll-ups.

Read-only. Reporting never mutates state and never persists directly — it
reads through the Repository and returns plain dicts/Decimals.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from orderflow import config
from orderflow.storage import Repository
from orderflow.models import Order, OrderStatus
from orderflow.services import orders as order_service

_CENTS = Decimal("0.01")


def _money(value) -> Decimal:
    return Decimal(str(value)).quantize(_CENTS, rounding=ROUND_HALF_UP)


def _counts_as_revenue(order: Order) -> bool:
    """Whether an order contributes to revenue figures."""
    if order.is_cancelled():
        return config.FEATURE_INCLUDE_CANCELLED_IN_REVENUE
    return True


def total_revenue(repo: Repository) -> Decimal:
    """Sum of order totals (incl. shipping) across all revenue-counting orders.

    Cancelled orders are excluded unless the corresponding feature flag is on.
    Returns a two-place Decimal.
    """
    total = Decimal("0")
    for order in repo.list_orders():
        if not order.lines:
            continue
        if not _counts_as_revenue(order):
            continue
        total += order_service.compute_totals(repo, order).total
    return _money(total)


def revenue_by_status(repo: Repository) -> dict[str, str]:
    """Revenue grouped by order status, as a {status: amount-string} dict."""
    buckets: dict[str, Decimal] = {}
    for order in repo.list_orders():
        if not order.lines:
            continue
        key = order.status.value
        amount = order_service.compute_totals(repo, order).total
        buckets[key] = buckets.get(key, Decimal("0")) + amount
    return {status: str(_money(amt)) for status, amt in buckets.items()}


def order_count(repo: Repository) -> int:
    """Number of orders that are not cancelled."""
    return sum(1 for o in repo.list_orders() if not o.is_cancelled())


def average_order_value(repo: Repository) -> Decimal:
    """Mean revenue-counting order total. Zero if there are none."""
    totals = [
        order_service.compute_totals(repo, o).total
        for o in repo.list_orders()
        if o.lines and _counts_as_revenue(o)
    ]
    if not totals:
        return _money("0")
    return _money(sum(totals) / Decimal(len(totals)))
