"""Tests for the pricing service."""

from decimal import Decimal

import pytest

from orderflow.models import Order, OrderLine, Customer
from orderflow.services import pricing


def _order(*lines):
    return Order(id="ORD-1", customer_id="C1", lines=list(lines))


def test_money_quantizes():
    assert pricing.money("1.005") == Decimal("1.01")  # ROUND_HALF_UP
    assert pricing.money(2) == Decimal("2.00")


def test_tier_discount_rate():
    assert pricing.tier_discount_rate(Customer(id="c", name="n", email="e@e.com", tier="gold")) == Decimal("0.10")
    assert pricing.tier_discount_rate(Customer(id="c", name="n", email="e@e.com", tier="silver")) == Decimal("0.05")
    assert pricing.tier_discount_rate(Customer(id="c", name="n", email="e@e.com")) == Decimal("0")


def test_compute_tax_uses_config_rate():
    # VAT_RATE default 0.06
    assert pricing.compute_tax(Decimal("100.00")) == Decimal("6.00")


def test_price_order_standard_customer():
    order = _order(OrderLine(sku="AB-100", quantity=2, unit_price=Decimal("10.00")))
    customer = Customer(id="C1", name="n", email="e@e.com", tier="standard")
    bd = pricing.price_order(order, customer, taxable_base=Decimal("20.00"))
    assert bd.subtotal == Decimal("20.00")
    assert bd.discount == Decimal("0.00")
    assert bd.tax == Decimal("1.20")
    assert bd.total == Decimal("21.20")


def test_price_order_gold_discount():
    order = _order(OrderLine(sku="AB-100", quantity=1, unit_price=Decimal("100.00")))
    customer = Customer(id="C1", name="n", email="e@e.com", tier="gold")
    bd = pricing.price_order(order, customer, taxable_base=Decimal("100.00"))
    assert bd.subtotal == Decimal("100.00")
    assert bd.discount == Decimal("10.00")
    # taxable base after discount = 90, tax = 5.40
    assert bd.tax == Decimal("5.40")
    assert bd.total == Decimal("95.40")


def test_price_empty_order_raises():
    with pytest.raises(ValueError):
        pricing.price_order(_order(), Customer(id="C1", name="n", email="e@e.com"), Decimal("0"))


def test_average_line_price():
    order = _order(
        OrderLine(sku="AB-100", quantity=2, unit_price=Decimal("10.00")),
        OrderLine(sku="AB-200", quantity=2, unit_price=Decimal("20.00")),
    )
    assert pricing.average_line_price(order) == Decimal("15.00")


def test_average_empty_raises():
    with pytest.raises(ValueError):
        pricing.average_line_price(_order())


def test_discount_per_unit():
    order = _order(OrderLine(sku="AB-100", quantity=2, unit_price=Decimal("100.00")))
    customer = Customer(id="C1", name="n", email="e@e.com", tier="gold")
    # subtotal 200, 10% discount = 20, over 2 units = 10.00 each.
    assert pricing.discount_per_unit(order, customer) == Decimal("10.00")
