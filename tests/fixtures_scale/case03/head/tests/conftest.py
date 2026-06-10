"""Shared pytest fixtures for the orderflow suite."""

from __future__ import annotations

from decimal import Decimal

import pytest

from orderflow.storage import Repository
from orderflow.models import Customer, Product, Order, OrderLine, OrderStatus


@pytest.fixture
def repo() -> Repository:
    """A fresh in-memory repository (no disk persistence)."""
    return Repository()


@pytest.fixture
def seeded_repo(repo: Repository) -> Repository:
    """A repository with a representative spread of customers and products."""
    repo.save_customer(
        Customer(id="C1", name="Ada", email="ada@example.com", tier="gold")
    )
    repo.save_customer(
        Customer(id="C2", name="Bo", email="bo@example.com", tier="silver")
    )
    repo.save_customer(
        Customer(id="C3", name="Cy", email="cy@example.com", tier="standard")
    )

    # on_hand vs reorder_level chosen so shortages differ:
    #   AB-100 shortage 2, AB-200 shortage 4, AB-300 shortage 1, AB-400 healthy
    repo.save_product(
        Product(sku="AB-100", name="Widget", unit_price=Decimal("19.99"),
                on_hand=3, reorder_level=5, weight_grams=200)
    )
    repo.save_product(
        Product(sku="AB-200", name="Gadget", unit_price=Decimal("9.50"),
                on_hand=1, reorder_level=5, weight_grams=120)
    )
    repo.save_product(
        Product(sku="AB-300", name="Gizmo", unit_price=Decimal("49.00"),
                on_hand=4, reorder_level=5, weight_grams=600)
    )
    repo.save_product(
        Product(sku="AB-400", name="Doohickey", unit_price=Decimal("4.25"),
                on_hand=50, reorder_level=5, taxable=False, weight_grams=30)
    )
    return repo


class FakeTransport:
    """A notification transport that records sends and can be told to fail."""

    def __init__(self, fail_for: set[str] | None = None):
        self.fail_for = fail_for or set()
        self.sent: list[tuple[str, str]] = []

    def send(self, recipient: str, message: str) -> None:
        from orderflow.services.notifications import NotificationError

        if recipient in self.fail_for:
            raise NotificationError(f"transport refused {recipient}")
        self.sent.append((recipient, message))


@pytest.fixture
def transport() -> FakeTransport:
    return FakeTransport()
