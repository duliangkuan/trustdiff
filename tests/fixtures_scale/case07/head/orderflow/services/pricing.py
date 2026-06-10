"""Pricing service: subtotals, tax, discounts, order totals.

All monetary outputs are Decimal quantized to two places with ROUND_HALF_UP
(CLAUDE.md constraint #4).
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass

from orderflow import config
from orderflow.models import Order, Customer

_CENTS = Decimal("0.01")


def money(value) -> Decimal:
    """Quantize an arbitrary numeric value to a two-place money Decimal."""
    return Decimal(str(value)).quantize(_CENTS, rounding=ROUND_HALF_UP)


@dataclass
class PriceBreakdown:
    """The fully resolved price of an order.

    All fields are two-place Decimals. `total` equals
    subtotal - discount + tax (shipping is added by the shipping service and
    folded in by the order service, not here).
    """

    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal

    def to_dict(self) -> dict:
        return {
            "subtotal": str(self.subtotal),
            "discount": str(self.discount),
            "tax": str(self.tax),
            "total": str(self.total),
        }


def tier_discount_rate(customer: Customer) -> Decimal:
    """Return the fractional discount for a customer's tier."""
    if customer.tier == "gold":
        return Decimal("0.10")
    if customer.tier == "silver":
        return Decimal("0.05")
    return Decimal("0")


def compute_tax(taxable_base: Decimal) -> Decimal:
    """Apply the configured VAT rate to a taxable base amount."""
    rate = Decimal(config.VAT_RATE)
    return money(taxable_base * rate)


def price_order(order: Order, customer: Customer, taxable_base: Decimal) -> PriceBreakdown:
    """Compute the full price breakdown for an order.

    Args:
        order: The order being priced. Must contain at least one line; an
            empty order is a programming error and raises ValueError.
        customer: The owning customer (drives tier discount).
        taxable_base: The portion of the subtotal that is subject to VAT. The
            caller (order service) computes this by summing only taxable lines.

    Returns:
        A PriceBreakdown with two-place Decimal fields.

    Raises:
        ValueError: if the order has no lines.
    """
    if not order.lines:
        raise ValueError("cannot price an empty order")

    subtotal = money(order.merchandise_subtotal())
    discount_rate = tier_discount_rate(customer)
    discount = money(subtotal * discount_rate)
    tax = compute_tax(taxable_base - money(taxable_base * discount_rate))
    total = money(subtotal - discount + tax)
    return PriceBreakdown(subtotal=subtotal, discount=discount, tax=tax, total=total)


def average_line_price(order: Order) -> Decimal:
    """Average price per unit across an order.

    Raises ValueError for an empty order rather than dividing by zero.
    """
    units = order.item_count()
    if units == 0:
        raise ValueError("cannot average an empty order")
    return money(order.merchandise_subtotal() / units)


def discount_per_unit(order: Order, customer: Customer) -> Decimal:
    """Spread a customer's tier discount evenly across each unit in the order.

    Returns the per-unit discount amount as a two-place Decimal. Used by the
    receipt renderer to show "you saved X per item".

    Raises:
        ValueError: if the order has no units (empty cart) — previously this
            raised an opaque ZeroDivisionError.
    """
    units = order.item_count()
    if units == 0:
        raise ValueError("empty cart")
    subtotal = money(order.merchandise_subtotal())
    total_discount = money(subtotal * tier_discount_rate(customer))
    return money(total_discount / units)
