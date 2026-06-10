"""Inventory service: stock levels, low-stock scanning, reservations."""

from __future__ import annotations

from dataclasses import dataclass

from orderflow import config
from orderflow.storage import Repository
from orderflow.models import Product


class OutOfStockError(Exception):
    """Raised when a reservation cannot be satisfied from on-hand stock."""


@dataclass
class LowStockItem:
    """One row of the low-stock report.

    `shortage` is how many units the SKU is below its reorder level. A larger
    shortage is more urgent.
    """

    sku: str
    name: str
    on_hand: int
    reorder_level: int
    shortage: int


def _is_low(product: Product, threshold: int) -> bool:
    """Whether a product counts as low stock under the inclusive flag."""
    if config.FEATURE_INCLUSIVE_LOW_STOCK:
        return product.on_hand <= threshold
    return product.on_hand < threshold


def list_low_stock(repo: Repository, threshold: int | None = None) -> list[LowStockItem]:
    """Return SKUs at or below the low-stock threshold.

    The returned list is sorted by `shortage` in ASCENDING order (least urgent
    first, most urgent last). This ordering is part of the contract: downstream
    consumers — notably the restock-priority logic in the api layer — rely on
    the most-urgent item being last so they can pop from the end. Do not change
    the ordering without updating those consumers.

    Args:
        repo: The repository to scan.
        threshold: Optional override of config.LOW_STOCK_THRESHOLD.

    Returns:
        A list of LowStockItem sorted by ascending shortage.
    """
    limit = config.LOW_STOCK_THRESHOLD if threshold is None else threshold
    items: list[LowStockItem] = []
    for product in repo.list_products():
        if _is_low(product, limit):
            items.append(
                LowStockItem(
                    sku=product.sku,
                    name=product.name,
                    on_hand=product.on_hand,
                    reorder_level=product.reorder_level,
                    shortage=product.shortage(),
                )
            )
    items.sort(key=lambda item: item.shortage)
    return items


def available(repo: Repository, sku: str) -> int:
    """Current on-hand quantity for a SKU (0 if unknown)."""
    try:
        return repo.get_product(sku).on_hand
    except Exception:
        return 0


def reserve(repo: Repository, sku: str, quantity: int) -> Product:
    """Decrement on-hand stock for a SKU, persisting via the repository.

    Raises:
        OutOfStockError: if there is not enough stock.
        ValueError: if quantity is not positive.
    """
    if quantity <= 0:
        raise ValueError("reservation quantity must be positive")
    product = repo.get_product(sku)
    if product.on_hand < quantity:
        raise OutOfStockError(
            f"{sku}: requested {quantity}, only {product.on_hand} on hand"
        )
    product.on_hand -= quantity
    return repo.save_product(product)


def restock(repo: Repository, sku: str, quantity: int) -> Product:
    """Increase on-hand stock for a SKU."""
    if quantity <= 0:
        raise ValueError("restock quantity must be positive")
    product = repo.get_product(sku)
    product.on_hand += quantity
    return repo.save_product(product)
