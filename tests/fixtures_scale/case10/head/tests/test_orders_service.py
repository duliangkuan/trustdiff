"""Tests for the order service."""

from decimal import Decimal

import pytest

from orderflow.models import OrderStatus
from orderflow.services import orders as order_service
from orderflow.services import inventory


def test_create_order_reserves_stock(seeded_repo):
    order = order_service.create_order(seeded_repo, "C1", [("AB-400", 5)])
    assert order.status == OrderStatus.PENDING
    assert order.id == "ORD-00001"
    assert inventory.available(seeded_repo, "AB-400") == 45


def test_create_order_captures_unit_price(seeded_repo):
    order = order_service.create_order(seeded_repo, "C1", [("AB-300", 1)])
    assert order.lines[0].unit_price == Decimal("49.00")


def test_create_order_empty_items_raises(seeded_repo):
    with pytest.raises(order_service.OrderError):
        order_service.create_order(seeded_repo, "C1", [])


def test_create_order_inactive_customer(seeded_repo):
    cust = seeded_repo.get_customer("C3")
    cust.is_active = False
    seeded_repo.save_customer(cust)
    with pytest.raises(order_service.OrderError):
        order_service.create_order(seeded_repo, "C3", [("AB-400", 1)])


def test_create_order_out_of_stock(seeded_repo):
    with pytest.raises(inventory.OutOfStockError):
        order_service.create_order(seeded_repo, "C1", [("AB-200", 99)])


def test_compute_totals_gold_with_shipping(seeded_repo):
    # gold customer C1, 1x AB-300 @ 49.00 (taxable). Below free-ship threshold.
    order = order_service.create_order(seeded_repo, "C1", [("AB-300", 1)])
    totals = order_service.compute_totals(seeded_repo, order)
    assert totals.subtotal == Decimal("49.00")
    assert totals.discount == Decimal("4.90")  # 10%
    # taxable base after discount = 44.10, tax = 2.646 -> 2.65
    assert totals.tax == Decimal("2.65")
    assert totals.shipping == Decimal("6.50")  # below 75
    assert totals.total == Decimal("53.25")


def test_compute_totals_free_shipping(seeded_repo):
    order = order_service.create_order(seeded_repo, "C3", [("AB-300", 2)])
    totals = order_service.compute_totals(seeded_repo, order)
    assert totals.subtotal == Decimal("98.00")
    assert totals.shipping == Decimal("0.00")


def test_nontaxable_line_excluded_from_tax(seeded_repo):
    # AB-400 is non-taxable.
    order = order_service.create_order(seeded_repo, "C3", [("AB-400", 4)])
    totals = order_service.compute_totals(seeded_repo, order)
    assert totals.tax == Decimal("0.00")


def test_confirm_order(seeded_repo):
    order = order_service.create_order(seeded_repo, "C1", [("AB-400", 1)])
    confirmed = order_service.confirm_order(seeded_repo, order.id)
    assert confirmed.status == OrderStatus.CONFIRMED


def test_confirm_non_pending_raises(seeded_repo):
    order = order_service.create_order(seeded_repo, "C1", [("AB-400", 1)])
    order_service.confirm_order(seeded_repo, order.id)
    with pytest.raises(order_service.OrderError):
        order_service.confirm_order(seeded_repo, order.id)


def test_cancel_returns_stock(seeded_repo):
    order = order_service.create_order(seeded_repo, "C1", [("AB-400", 5)])
    assert inventory.available(seeded_repo, "AB-400") == 45
    cancelled = order_service.cancel_order(seeded_repo, order.id)
    assert cancelled.status == OrderStatus.CANCELLED
    assert inventory.available(seeded_repo, "AB-400") == 50


def test_estimated_delivery_hours(seeded_repo, monkeypatch):
    # The shipping estimator is exercised in its own suite; here we only check
    # the order service wires through the order lookup and returns the figure.
    order = order_service.create_order(seeded_repo, "C1", [("AB-400", 1)])
    monkeypatch.setattr(
        "orderflow.services.orders.shipping.estimate_eta_hours",
        lambda distance_km, carrier_timeout=None: 5.0,
    )
    assert order_service.estimated_delivery_hours(seeded_repo, order.id, 120.0) == 5.0
