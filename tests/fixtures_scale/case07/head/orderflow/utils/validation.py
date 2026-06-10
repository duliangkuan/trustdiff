"""Input validation helpers."""

from __future__ import annotations

import re

# Local-part allows letters, digits, dot, underscore, percent, plus and hyphen.
# Domain is a dotted sequence of alphanumeric/hyphen labels with a 2+ char TLD.
_EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
)

_SKU_RE = re.compile(r"^[A-Z]{2,4}-[0-9]{3,6}$")


class ValidationError(ValueError):
    """Raised when a value fails validation."""


def validate_email(email: str) -> bool:
    """Return True if `email` is a syntactically valid address.

    The local part accepts plus-addressing (e.g. ``user+tag@example.com``),
    which many providers use for filtering. This does not perform DNS or
    deliverability checks — purely a syntax gate.
    """
    if not isinstance(email, str):
        return False
    return bool(_EMAIL_RE.match(email.strip()))


def validate_sku(sku: str) -> bool:
    """Return True if `sku` matches the canonical SKU format (e.g. AB-1234)."""
    if not isinstance(sku, str):
        return False
    return bool(_SKU_RE.match(sku.strip()))


def require_email(email: str) -> str:
    """Return the trimmed email or raise ValidationError."""
    cleaned = (email or "").strip()
    if not validate_email(cleaned):
        raise ValidationError(f"invalid email: {email!r}")
    return cleaned
