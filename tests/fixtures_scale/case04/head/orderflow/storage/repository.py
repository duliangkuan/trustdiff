"""The Repository — orderflow's single persistence gateway.

Per CLAUDE.md constraint #1, every durable read and write in the system goes
through this class. No other module opens a data file directly.

The default backend is an in-memory store seeded from / flushed to a single
JSON document on disk. The on-disk format is an implementation detail; callers
only ever see model objects.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from orderflow.models import Customer, Product, Order


class NotFoundError(KeyError):
    """Raised when a lookup by id finds nothing."""


class Repository:
    """In-memory repository with optional JSON-file persistence.

    Args:
        path: Optional path to a JSON document. If given and the file exists,
            it is loaded on construction. `flush()` writes back to it.
    """

    def __init__(self, path: Optional[str] = None) -> None:
        self._path = path
        self._customers: dict[str, Customer] = {}
        self._products: dict[str, Product] = {}
        self._orders: dict[str, Order] = {}
        if path and os.path.exists(path):
            self._load(path)

    # --- customers ---------------------------------------------------------

    def save_customer(self, customer: Customer) -> Customer:
        self._customers[customer.id] = customer
        return customer

    def get_customer(self, customer_id: str) -> Customer:
        try:
            return self._customers[customer_id]
        except KeyError:
            raise NotFoundError(f"customer {customer_id!r} not found")

    def list_customers(self) -> list[Customer]:
        return list(self._customers.values())

    # --- products ----------------------------------------------------------

    def save_product(self, product: Product) -> Product:
        self._products[product.sku] = product
        return product

    def get_product(self, sku: str) -> Product:
        try:
            return self._products[sku]
        except KeyError:
            raise NotFoundError(f"product {sku!r} not found")

    def list_products(self) -> list[Product]:
        return list(self._products.values())

    # --- orders ------------------------------------------------------------

    def save_order(self, order: Order) -> Order:
        self._orders[order.id] = order
        return order

    def get_order(self, order_id: str) -> Order:
        try:
            return self._orders[order_id]
        except KeyError:
            raise NotFoundError(f"order {order_id!r} not found")

    def list_orders(self) -> list[Order]:
        return list(self._orders.values())

    # --- persistence -------------------------------------------------------

    def flush(self) -> None:
        """Write the current state back to the JSON document, if configured."""
        if not self._path:
            return
        doc = {
            "customers": [c.to_dict() for c in self._customers.values()],
            "products": [p.to_dict() for p in self._products.values()],
            "orders": [o.to_dict() for o in self._orders.values()],
        }
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2)

    def _load(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        for raw in doc.get("customers", []):
            c = Customer.from_dict(raw)
            self._customers[c.id] = c
        for raw in doc.get("products", []):
            p = Product.from_dict(raw)
            self._products[p.sku] = p
        for raw in doc.get("orders", []):
            o = Order.from_dict(raw)
            self._orders[o.id] = o
