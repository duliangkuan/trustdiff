"""Integration tests for the api handlers (cross-service orchestration)."""

from decimal import Decimal

from orderflow.api import handlers
from orderflow.services import orders as order_service


def test_place_order_handler_success(seeded_repo):
    resp = handlers.place_order_handler(seeded_repo, "C1", [("AB-300", 1)])
    assert resp["ok"] is True
    assert resp["order"]["customer_id"] == "C1"
    assert resp["totals"]["total"] == "53.25"


def test_place_order_handler_out_of_stock(seeded_repo):
    resp = handlers.place_order_handler(seeded_repo, "C1", [("AB-200", 99)])
    assert resp["ok"] is False
    assert "on hand" in resp["error"]


def test_restock_priorities_most_urgent_first(seeded_repo):
    """The handler relies on inventory.list_low_stock ascending ordering and
    must surface the MOST urgent SKU first."""
    rows = handlers.restock_priorities(seeded_repo, top_n=3)
    skus = [r["sku"] for r in rows]
    # AB-200 shortage 4 (most urgent) -> first; AB-300 shortage 1 -> last.
    assert skus[0] == "AB-200"
    assert skus[-1] == "AB-300"
    # Shortages must be descending in the prioritised view.
    shortages = [r["shortage"] for r in rows]
    assert shortages == sorted(shortages, reverse=True)


def test_restock_priorities_respects_top_n(seeded_repo):
    rows = handlers.restock_priorities(seeded_repo, top_n=2)
    assert len(rows) == 2
    assert rows[0]["sku"] == "AB-200"


def test_notify_customers_all_ok(seeded_repo, transport):
    resp = handlers.notify_customers_handler(
        seeded_repo, transport, ["C1", "C2", "C3"], "sale!"
    )
    assert resp["ok"] is True
    assert resp["sent_count"] == 3
    assert "failed_recipients" not in resp


def test_notify_customers_reports_failures(seeded_repo, transport):
    """A failed send must be reported, not silently dropped."""
    transport.fail_for = {"bo@example.com"}
    resp = handlers.notify_customers_handler(
        seeded_repo, transport, ["C1", "C2", "C3"], "sale!"
    )
    assert resp["ok"] is False
    assert resp["failed_recipients"] == ["bo@example.com"]
    assert resp["failed_count"] == 1
    assert resp["sent_count"] == 2


def test_notify_skips_invalid_emails(seeded_repo, transport):
    cust = seeded_repo.get_customer("C3")
    cust.email = "broken-email"
    seeded_repo.save_customer(cust)
    resp = handlers.notify_customers_handler(
        seeded_repo, transport, ["C1", "C3"], "hi"
    )
    # Only C1 has a valid email.
    assert resp["sent_count"] == 1


def test_revenue_summary_handler(seeded_repo):
    order_service.create_order(seeded_repo, "C1", [("AB-300", 1)])
    order_service.create_order(seeded_repo, "C3", [("AB-300", 2)])
    resp = handlers.revenue_summary_handler(seeded_repo)
    assert resp["ok"] is True
    assert resp["order_count"] == 2
    assert Decimal(resp["total_revenue"]) > Decimal("0")
