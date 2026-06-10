"""Tests for the shipping service."""

from decimal import Decimal

from orderflow.models import Order
from orderflow.services import shipping


def test_free_shipping_above_threshold():
    assert shipping.shipping_fee(Decimal("75.00")) == Decimal("0.00")
    assert shipping.shipping_fee(Decimal("120.00")) == Decimal("0.00")


def test_flat_fee_below_threshold():
    assert shipping.shipping_fee(Decimal("74.99")) == Decimal("6.50")
    assert shipping.shipping_fee(Decimal("0.00")) == Decimal("6.50")


def test_proportional_fee_rounds_half_up():
    # 10.05 * 12.5% = 1.25625 -> 1.26 (was truncating to 1.25 before the fix).
    assert shipping.proportional_shipping_fee(Decimal("10.05"), Decimal("0.125")) == Decimal("1.26")
    assert shipping.proportional_shipping_fee(Decimal("10.00"), Decimal("0.125")) == Decimal("1.25")
    assert shipping.proportional_shipping_fee(Decimal("0.00"), Decimal("0.125")) == Decimal("0.00")


def test_weight_surcharge_zero_in_base():
    order = Order(id="ORD-1", customer_id="C1")
    assert shipping.weight_surcharge(order) == Decimal("0.00")


def test_estimate_eta_grows_with_distance():
    near = shipping.estimate_eta_hours(60.0)
    far = shipping.estimate_eta_hours(600.0)
    assert far > near


def test_estimate_eta_uses_seconds_timeout():
    # carrier_timeout is in seconds; a 3600s timeout adds ~1 hour handling.
    eta = shipping.estimate_eta_hours(0.0, carrier_timeout=3600)
    assert abs(eta - 2.0) < 1e-9


def test_carrier_poll_budget():
    assert shipping.carrier_poll_budget(30) == 6
    assert shipping.carrier_poll_budget(2) == 1  # floor of 1
