"""Order service: create, price, confirm and summarise orders.

This is the orchestration core of the services layer. It composes pricing,
inventory and shipping, and persists exclusively through the Repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from orderflow import config
from orderflow.models import Order, OrderLine, OrderStatus, Customer, Product
from orderflow.storage import Repository, NotFoundError
from orderflow.services import pricing, inventory, shipping
from orderflow.utils.timeutil import utc_now, to_iso


class OrderError(Exception):
    """Raised for invalid order operations."""


@dataclass
class OrderTotals:
    """Money summary for an order, all two-place Decimals."""

    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    shipping: Decimal
    total: Decimal

    def to_dict(self) -> dict:
        return {
            "subtotal": str(self.subtotal),
            "discount": str(self.discount),
            "tax": str(self.tax),
            "shipping": str(self.shipping),
            "total": str(self.total),
        }


def _new_order_id(repo: Repository) -> str:
    return f"ORD-{len(repo.list_orders()) + 1:05d}"


def _taxable_base(repo: Repository, lines: list[OrderLine]) -> Decimal:
    """Sum of line totals for taxable products only."""
    base = Decimal("0")
    for line in lines:
        try:
            product = repo.get_product(line.sku)
        except NotFoundError:
            continue
        if product.taxable:
            base += line.line_total()
    return base


def create_order(
    repo: Repository,
    customer_id: str,
    items: list[tuple[str, int]],
    shipping_address: str = "",
) -> Order:
    """Create and persist a new order for a customer.

    Args:
        repo: Repository.
        customer_id: Owning customer; must exist and be active.
        items: List of (sku, quantity) pairs. Each SKU must exist and have
            enough stock; stock is reserved as part of creation.
        shipping_address: Optional address string.

    Returns:
        The persisted Order in PENDING status.

    Raises:
        OrderError: if the customer is missing/inactive or items is empty.
        NotFoundError: if a SKU does not exist.
        inventory.OutOfStockError: if stock is insufficient.
    """
    if not items:
        raise OrderError("cannot create an order with no items")
    customer = _require_active_customer(repo, customer_id)

    lines = _build_lines(repo, items)
    _reserve_lines(repo, lines)

    order = Order(
        id=_new_order_id(repo),
        customer_id=customer.id,
        lines=lines,
        status=OrderStatus.PENDING,
        created_at=to_iso(utc_now()),
        shipping_address=shipping_address,
    )
    return repo.save_order(order)


def _require_active_customer(repo: Repository, customer_id: str) -> Customer:
    """Fetch a customer, asserting they exist and are allowed to order."""
    customer = repo.get_customer(customer_id)
    if not customer.is_active:
        raise OrderError(f"customer {customer_id} is inactive")
    return customer


def _build_lines(repo: Repository, items: list[tuple[str, int]]) -> list[OrderLine]:
    """Resolve (sku, qty) pairs into order lines, capturing current prices.

    Prices are captured here so later catalogue changes never rewrite history.
    """
    lines: list[OrderLine] = []
    for sku, quantity in items:
        product = repo.get_product(sku)
        lines.append(OrderLine(sku=sku, quantity=quantity, unit_price=product.unit_price))
    return lines


def _reserve_lines(repo: Repository, lines: list[OrderLine]) -> None:
    """Reserve stock for every line. Call only after all lines validate."""
    for line in lines:
        inventory.reserve(repo, line.sku, line.quantity)


def compute_totals(repo: Repository, order: Order) -> OrderTotals:
    """Compute the full money breakdown for an order, including shipping."""
    customer = repo.get_customer(order.customer_id)
    taxable_base = _taxable_base(repo, order.lines)
    breakdown = pricing.price_order(order, customer, taxable_base)
    ship = shipping.shipping_fee(breakdown.subtotal)
    total = pricing.money(breakdown.total + ship)
    return OrderTotals(
        subtotal=breakdown.subtotal,
        discount=breakdown.discount,
        tax=breakdown.tax,
        shipping=ship,
        total=total,
    )


def confirm_order(repo: Repository, order_id: str) -> Order:
    """Transition a PENDING order to CONFIRMED."""
    order = repo.get_order(order_id)
    if order.status != OrderStatus.PENDING:
        raise OrderError(f"order {order_id} is not pending (is {order.status.value})")
    order.status = OrderStatus.CONFIRMED
    return repo.save_order(order)


def cancel_order(repo: Repository, order_id: str) -> Order:
    """Cancel an order and return reserved stock to inventory."""
    order = repo.get_order(order_id)
    if order.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
        raise OrderError(f"order {order_id} already in transit; cannot cancel")
    if not order.is_cancelled():
        for line in order.lines:
            try:
                inventory.restock(repo, line.sku, line.quantity)
            except NotFoundError:
                continue
    order.status = OrderStatus.CANCELLED
    return repo.save_order(order)


def estimated_delivery_hours(repo: Repository, order_id: str, distance_km: float) -> float:
    """Estimate delivery time in hours for an order at a given distance.

    Delegates to the shipping service for the actual estimate. We pass the
    standard carrier handoff timeout from config (in SECONDS) so the estimate
    accounts for carrier acknowledgement latency.
    """
    repo.get_order(order_id)  # validate existence
    return shipping.estimate_eta_hours(distance_km, carrier_timeout=config.HTTP_TIMEOUT_S)
