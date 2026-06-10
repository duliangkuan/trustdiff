"""Tests for the reporting service."""

from decimal import Decimal

from orderflow.services import orders as order_service
from orderflow.services import reporting


def test_total_revenue_sums_orders(seeded_repo):
    order_service.create_order(seeded_repo, "C1", [("AB-300", 1)])  # total 54.57
    order_service.create_order(seeded_repo, "C3", [("AB-300", 2)])  # free ship
    total = reporting.total_revenue(seeded_repo)
    assert total > Decimal("0")


def test_cancelled_excluded_by_default(seeded_repo):
    o1 = order_service.create_order(seeded_repo, "C1", [("AB-300", 1)])
    before = reporting.total_revenue(seeded_repo)
    order_service.cancel_order(seeded_repo, o1.id)
    after = reporting.total_revenue(seeded_repo)
    assert after < before


def test_order_count_excludes_cancelled(seeded_repo):
    o1 = order_service.create_order(seeded_repo, "C1", [("AB-400", 1)])
    order_service.create_order(seeded_repo, "C3", [("AB-400", 1)])
    assert reporting.order_count(seeded_repo) == 2
    order_service.cancel_order(seeded_repo, o1.id)
    assert reporting.order_count(seeded_repo) == 1


def test_revenue_by_status(seeded_repo):
    order_service.create_order(seeded_repo, "C1", [("AB-300", 1)])
    by_status = reporting.revenue_by_status(seeded_repo)
    assert "pending" in by_status


def test_average_order_value_zero_when_empty(seeded_repo):
    assert reporting.average_order_value(seeded_repo) == Decimal("0.00")


def test_average_order_value(seeded_repo):
    order_service.create_order(seeded_repo, "C3", [("AB-300", 1)])
    avg = reporting.average_order_value(seeded_repo)
    assert avg > Decimal("0")


def test_monthly_revenue_groups_by_month(seeded_repo):
    o1 = order_service.create_order(seeded_repo, "C3", [("AB-300", 1)])
    o2 = order_service.create_order(seeded_repo, "C3", [("AB-300", 1)])
    # Pin the created_at months deterministically.
    o1.created_at = "2026-01-15T10:00:00+00:00"
    seeded_repo.save_order(o1)
    o2.created_at = "2026-02-03T09:30:00+00:00"
    seeded_repo.save_order(o2)

    monthly = reporting.monthly_revenue(seeded_repo)
    assert set(monthly) == {"2026-01", "2026-02"}
    assert Decimal(monthly["2026-01"]) > Decimal("0")


def test_monthly_revenue_skips_orders_without_timestamp(seeded_repo):
    o1 = order_service.create_order(seeded_repo, "C3", [("AB-300", 1)])
    o1.created_at = ""
    seeded_repo.save_order(o1)
    assert reporting.monthly_revenue(seeded_repo) == {}
