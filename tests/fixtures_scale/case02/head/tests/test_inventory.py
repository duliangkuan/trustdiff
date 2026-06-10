"""Tests for the inventory service."""

import pytest

from orderflow.services import inventory


def test_list_low_stock_finds_low_items(seeded_repo):
    low = inventory.list_low_stock(seeded_repo)
    skus = {item.sku for item in low}
    # AB-100 (3), AB-200 (1), AB-300 (4) are low; AB-400 (50) is not.
    assert skus == {"AB-100", "AB-200", "AB-300"}


def test_list_low_stock_sorted_ascending_by_shortage(seeded_repo):
    """Contract: ascending by shortage, most urgent LAST."""
    low = inventory.list_low_stock(seeded_repo)
    shortages = [item.shortage for item in low]
    assert shortages == sorted(shortages)
    # AB-300 shortage 1 first, AB-200 shortage 4 last.
    assert low[0].sku == "AB-300"
    assert low[-1].sku == "AB-200"


def test_list_low_stock_threshold_override(seeded_repo):
    low = inventory.list_low_stock(seeded_repo, threshold=1)
    skus = {item.sku for item in low}
    assert skus == {"AB-200"}  # only on_hand <= 1


def test_available(seeded_repo):
    assert inventory.available(seeded_repo, "AB-100") == 3
    assert inventory.available(seeded_repo, "nope") == 0


def test_reserve_decrements(seeded_repo):
    inventory.reserve(seeded_repo, "AB-400", 10)
    assert inventory.available(seeded_repo, "AB-400") == 40


def test_reserve_insufficient_raises(seeded_repo):
    with pytest.raises(inventory.OutOfStockError):
        inventory.reserve(seeded_repo, "AB-200", 5)


def test_reserve_nonpositive_raises(seeded_repo):
    with pytest.raises(ValueError):
        inventory.reserve(seeded_repo, "AB-100", 0)


def test_restock_increments(seeded_repo):
    inventory.restock(seeded_repo, "AB-100", 7)
    assert inventory.available(seeded_repo, "AB-100") == 10
