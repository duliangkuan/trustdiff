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


def test_weight_surcharge_zero_in_base():
    order = Order(id="ORD-1", customer_id="C1")
    assert shipping.weight_surcharge(order) == Decimal("0.00")


def test_estimate_eta_grows_with_distance():
    near = shipping.estimate_eta_hours(60.0)
    far = shipping.estimate_eta_hours(600.0)
    assert far > near


def test_estimate_eta_uses_millisecond_timeout():
    # carrier_timeout is now in milliseconds; 3_600_000 ms == 1 h handling.
    eta = shipping.estimate_eta_hours(0.0, carrier_timeout=3_600_000)
    assert abs(eta - 2.0) < 1e-9


def test_estimate_eta_ms_matches_hours():
    hours = shipping.estimate_eta_hours(120.0, carrier_timeout=3_600_000)
    ms = shipping.estimate_eta_ms(120.0, carrier_timeout=3_600_000)
    assert abs(ms - hours * 3600_000) < 1.0


def test_format_eta_string():
    # 120 km / 60 = 2h, + handling (1 + 3_600_000ms->1h) = 2h => total 4h 0m.
    assert shipping.format_eta(120.0, carrier_timeout=3_600_000) == "4h 0m"
    # 30 km / 60 = 0.5h = 30m, + 1h base handling at 0 ms => 1h 30m.
    assert shipping.format_eta(30.0, carrier_timeout=0) == "1h 30m"


def test_carrier_poll_budget():
    assert shipping.carrier_poll_budget(30) == 6
    assert shipping.carrier_poll_budget(2) == 1  # floor of 1
