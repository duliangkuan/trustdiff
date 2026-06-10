"""Customer model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Customer:
    """A registered customer.

    Attributes:
        id: Stable customer identifier.
        name: Display name.
        email: Contact email. Validated at the service boundary, not here.
        tier: One of "standard", "silver", "gold". Affects nothing on the
            model itself; pricing reads it.
        is_active: Inactive customers cannot place new orders.
    """

    id: str
    name: str
    email: str
    tier: str = "standard"
    is_active: bool = True
    tags: list[str] = field(default_factory=list)

    def is_premium(self) -> bool:
        """Return True for tiers that receive premium handling."""
        return self.tier in ("silver", "gold")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "tier": self.tier,
            "is_active": self.is_active,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "Customer":
        return cls(
            id=raw["id"],
            name=raw["name"],
            email=raw["email"],
            tier=raw.get("tier", "standard"),
            is_active=raw.get("is_active", True),
            tags=list(raw.get("tags", [])),
        )
