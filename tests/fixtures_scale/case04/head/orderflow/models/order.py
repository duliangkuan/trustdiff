"""Order model and its line items."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    """Lifecycle of an order."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderLine:
    """A single line in an order.

    `unit_price` is captured at order time so later price changes do not
    retroactively alter historical orders.
    """

    sku: str
    quantity: int
    unit_price: Decimal

    def line_total(self) -> Decimal:
        """Quantity times captured unit price (un-quantized)."""
        return self.unit_price * self.quantity

    def to_dict(self) -> dict:
        return {
            "sku": self.sku,
            "quantity": self.quantity,
            "unit_price": str(self.unit_price),
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "OrderLine":
        return cls(
            sku=raw["sku"],
            quantity=raw["quantity"],
            unit_price=Decimal(str(raw["unit_price"])),
        )


@dataclass
class Order:
    """A customer order.

    Attributes:
        id: Stable order identifier.
        customer_id: Owning customer.
        lines: Order lines, in the order they were added.
        status: Current lifecycle status.
        created_at: ISO-8601 UTC timestamp string.
        shipping_address: Free-form address string.
    """

    id: str
    customer_id: str
    lines: list[OrderLine] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    created_at: str = ""
    shipping_address: str = ""

    def merchandise_subtotal(self) -> Decimal:
        """Sum of all line totals, un-quantized.

        Quantization to two places happens in the pricing service, which owns
        money presentation.
        """
        total = Decimal("0")
        for line in self.lines:
            total += line.line_total()
        return total

    def item_count(self) -> int:
        return sum(line.quantity for line in self.lines)

    def is_cancelled(self) -> bool:
        return self.status == OrderStatus.CANCELLED

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "lines": [line.to_dict() for line in self.lines],
            "status": self.status.value,
            "created_at": self.created_at,
            "shipping_address": self.shipping_address,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "Order":
        return cls(
            id=raw["id"],
            customer_id=raw["customer_id"],
            lines=[OrderLine.from_dict(x) for x in raw.get("lines", [])],
            status=OrderStatus(raw.get("status", "pending")),
            created_at=raw.get("created_at", ""),
            shipping_address=raw.get("shipping_address", ""),
        )
