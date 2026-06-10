"""Time helpers. Everything here is UTC (CLAUDE.md constraint #3)."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def to_iso(dt: datetime) -> str:
    """Serialize a datetime to an ISO-8601 string.

    Naive datetimes are assumed to already be UTC and are tagged as such.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def parse_iso(text: str) -> datetime:
    """Parse an ISO-8601 string back into a UTC datetime."""
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
