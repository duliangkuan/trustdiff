"""Domain models for orderflow.

Plain dataclasses with a little behaviour. No persistence logic lives here —
that belongs to the Repository.
"""

from orderflow.models.customer import Customer
from orderflow.models.product import Product
from orderflow.models.order import Order, OrderLine, OrderStatus

__all__ = [
    "Customer",
    "Product",
    "Order",
    "OrderLine",
    "OrderStatus",
]
