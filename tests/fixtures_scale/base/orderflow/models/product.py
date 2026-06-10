"""Product / SKU model."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:
    """A sellable product.

    Attributes:
        sku: Stable stock-keeping unit identifier.
        name: Display name.
        unit_price: Price per unit as a Decimal. Always two decimal places
            once it crosses a service boundary.
        on_hand: Current quantity in the warehouse.
        reorder_level: When on_hand drops to/below this, the SKU is a restock
            candidate.
        taxable: Whether VAT applies to this product.
        weight_grams: Shipping weight, used by the shipping service.
    """

    sku: str
    name: str
    unit_price: Decimal
    on_hand: int = 0
    reorder_level: int = 5
    taxable: bool = True
    weight_grams: int = 0

    def shortage(self) -> int:
        """Units below the reorder level (0 if at or above it)."""
        gap = self.reorder_level - self.on_hand
        return gap if gap > 0 else 0

    def to_dict(self) -> dict:
        return {
            "sku": self.sku,
            "name": self.name,
            "unit_price": str(self.unit_price),
            "on_hand": self.on_hand,
            "reorder_level": self.reorder_level,
            "taxable": self.taxable,
            "weight_grams": self.weight_grams,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "Product":
        return cls(
            sku=raw["sku"],
            name=raw["name"],
            unit_price=Decimal(str(raw["unit_price"])),
            on_hand=raw.get("on_hand", 0),
            reorder_level=raw.get("reorder_level", 5),
            taxable=raw.get("taxable", True),
            weight_grams=raw.get("weight_grams", 0),
        )
