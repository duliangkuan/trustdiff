"""Tests for the domain models."""

from decimal import Decimal

from orderflow.models import Customer, Product, Order, OrderLine, OrderStatus


def test_customer_premium_tiers():
    assert Customer(id="x", name="X", email="x@e.com", tier="gold").is_premium()
    assert Customer(id="x", name="X", email="x@e.com", tier="silver").is_premium()
    assert not Customer(id="x", name="X", email="x@e.com", tier="standard").is_premium()


def test_customer_roundtrip():
    c = Customer(id="C9", name="Zed", email="z@e.com", tier="silver", tags=["vip"])
    assert Customer.from_dict(c.to_dict()) == c


def test_product_shortage():
    p = Product(sku="AB-100", name="W", unit_price=Decimal("1.00"),
                on_hand=2, reorder_level=5)
    assert p.shortage() == 3
    healthy = Product(sku="AB-101", name="W", unit_price=Decimal("1.00"),
                      on_hand=10, reorder_level=5)
    assert healthy.shortage() == 0


def test_product_roundtrip():
    p = Product(sku="AB-200", name="G", unit_price=Decimal("9.50"), on_hand=4)
    assert Product.from_dict(p.to_dict()) == p


def test_order_line_total():
    line = OrderLine(sku="AB-100", quantity=3, unit_price=Decimal("2.50"))
    assert line.line_total() == Decimal("7.50")


def test_order_subtotal_and_count():
    order = Order(
        id="ORD-1",
        customer_id="C1",
        lines=[
            OrderLine(sku="AB-100", quantity=2, unit_price=Decimal("19.99")),
            OrderLine(sku="AB-200", quantity=1, unit_price=Decimal("9.50")),
        ],
    )
    assert order.merchandise_subtotal() == Decimal("49.48")
    assert order.item_count() == 3


def test_order_status_default_and_cancel():
    order = Order(id="ORD-2", customer_id="C1")
    assert order.status == OrderStatus.PENDING
    assert not order.is_cancelled()
    order.status = OrderStatus.CANCELLED
    assert order.is_cancelled()


def test_order_roundtrip():
    order = Order(
        id="ORD-3",
        customer_id="C2",
        lines=[OrderLine(sku="AB-100", quantity=1, unit_price=Decimal("19.99"))],
        status=OrderStatus.CONFIRMED,
        created_at="2026-01-01T00:00:00+00:00",
    )
    assert Order.from_dict(order.to_dict()) == order
