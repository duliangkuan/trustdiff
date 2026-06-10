"""Text formatting helpers."""

from __future__ import annotations

import re

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")

_UNITS = ("B", "KB", "MB", "GB", "TB")


def format_size(num_bytes: int) -> str:
    """Format a byte count as a human-readable size string.

    Uses 1024-based units. The result has at most one decimal place and is
    suffixed with one of B/KB/MB/GB/TB. Examples:

        format_size(0)        -> "0 B"
        format_size(1536)     -> "1.5 KB"
        format_size(1048576)  -> "1.0 MB"

    Args:
        num_bytes: A non-negative byte count.

    Returns:
        A formatted size string.
    """
    if num_bytes < 0:
        raise ValueError("num_bytes must be non-negative")
    size = float(num_bytes)
    for unit in _UNITS:
        if size < 1024 or unit == _UNITS[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    # Unreachable, but keeps type-checkers happy.
    return f"{size:.1f} {_UNITS[-1]}"


def slugify(text: str) -> str:
    """Lowercase, strip non-alphanumerics, collapse to single hyphens."""
    lowered = text.strip().lower()
    slug = _SLUG_STRIP.sub("-", lowered)
    return slug.strip("-")


def truncate(text: str, limit: int, ellipsis: str = "...") -> str:
    """Truncate text to `limit` characters, appending an ellipsis if cut.

    The returned string (including the ellipsis) never exceeds `limit`.
    """
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    keep = max(0, limit - len(ellipsis))
    return text[:keep] + ellipsis
