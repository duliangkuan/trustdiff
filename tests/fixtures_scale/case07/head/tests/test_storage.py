"""Tests for the Repository persistence gateway."""

import os

import pytest

from decimal import Decimal

from orderflow.storage import Repository, NotFoundError
from orderflow.models import Customer, Product, Order, OrderLine


def test_customer_save_get(repo):
    c = Customer(id="C1", name="Ada", email="ada@e.com")
    repo.save_customer(c)
    assert repo.get_customer("C1") is c


def test_get_missing_raises(repo):
    with pytest.raises(NotFoundError):
        repo.get_customer("nope")
    with pytest.raises(NotFoundError):
        repo.get_product("nope")
    with pytest.raises(NotFoundError):
        repo.get_order("nope")


def test_lists(seeded_repo):
    assert len(seeded_repo.list_customers()) == 3
    assert len(seeded_repo.list_products()) == 4
    assert seeded_repo.list_orders() == []


def test_flush_and_reload(tmp_path):
    path = os.path.join(str(tmp_path), "store.json")
    repo = Repository(path)
    repo.save_customer(Customer(id="C1", name="Ada", email="ada@e.com", tier="gold"))
    repo.save_product(Product(sku="AB-100", name="W", unit_price=Decimal("19.99"), on_hand=3))
    repo.save_order(
        Order(id="ORD-1", customer_id="C1",
              lines=[OrderLine(sku="AB-100", quantity=1, unit_price=Decimal("19.99"))])
    )
    repo.flush()

    reloaded = Repository(path)
    assert reloaded.get_customer("C1").tier == "gold"
    assert reloaded.get_product("AB-100").unit_price == Decimal("19.99")
    assert reloaded.get_order("ORD-1").lines[0].quantity == 1


def test_flush_without_path_is_noop(repo):
    repo.save_customer(Customer(id="C1", name="Ada", email="ada@e.com"))
    repo.flush()  # should not raise
