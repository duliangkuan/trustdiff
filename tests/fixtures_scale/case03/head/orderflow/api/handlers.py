"""API handlers — orchestrate services into request-shaped operations.

Handlers return plain JSON-serializable dicts. They are the integration point
where several services come together, so they encode a few cross-service
assumptions (documented inline).
"""

from __future__ import annotations

from decimal import Decimal

from orderflow.storage import Repository, NotFoundError
from orderflow.services import (
    orders as order_service,
    inventory,
    notifications,
    reporting,
)
from orderflow.utils.validation import validate_email


def place_order_handler(
    repo: Repository,
    customer_id: str,
    items: list[tuple[str, int]],
    shipping_address: str = "",
) -> dict:
    """Create an order and return its summary with computed totals."""
    try:
        order = order_service.create_order(repo, customer_id, items, shipping_address)
    except (order_service.OrderError, inventory.OutOfStockError, NotFoundError) as exc:
        return {"ok": False, "error": str(exc)}
    totals = order_service.compute_totals(repo, order)
    return {
        "ok": True,
        "order": order.to_dict(),
        "totals": totals.to_dict(),
    }


def restock_priorities(repo: Repository, top_n: int = 3) -> list[dict]:
    """Return the `top_n` most urgent SKUs to restock, most-urgent first.

    This relies on the contract of ``inventory.list_low_stock``: that function
    returns items sorted by ascending shortage (most urgent LAST). We therefore
    take items from the END of that list to get the most urgent first. If the
    upstream ordering ever changes, this prioritisation breaks silently.
    """
    low = inventory.list_low_stock(repo)
    # Most urgent are at the tail; reverse-slice the last top_n.
    most_urgent = list(reversed(low[-top_n:]))
    return [
        {
            "sku": item.sku,
            "name": item.name,
            "shortage": item.shortage,
            "on_hand": item.on_hand,
        }
        for item in most_urgent
    ]


def notify_customers_handler(
    repo: Repository,
    transport,
    customer_ids: list[str],
    message: str,
) -> dict:
    """Notify a set of customers and report the outcome honestly.

    Any recipient whose send failed is surfaced in the response under
    "failed_recipients", and "ok" is False if there were any failures. This
    failure-reporting path exists precisely so that lost notifications are
    visible rather than silent.
    """
    recipients: list[str] = []
    for cid in customer_ids:
        try:
            customer = repo.get_customer(cid)
        except NotFoundError:
            continue
        if validate_email(customer.email):
            recipients.append(customer.email)

    result = notifications.send_batch(transport, recipients, message)

    response = {
        "ok": result.all_ok,
        "sent_count": len(result.sent),
    }
    if not result.all_ok:
        # Failure reporting branch — surfaces dropped notifications.
        response["failed_recipients"] = list(result.failed)
        response["failed_count"] = len(result.failed)
    return response


def revenue_summary_handler(repo: Repository) -> dict:
    """Return a small revenue dashboard payload."""
    return {
        "ok": True,
        "total_revenue": str(reporting.total_revenue(repo)),
        "order_count": reporting.order_count(repo),
        "average_order_value": str(reporting.average_order_value(repo)),
        "by_status": reporting.revenue_by_status(repo),
    }
