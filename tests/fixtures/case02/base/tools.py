"""Misc formatting tools."""

from http_client import HttpClient


def format_size(num_bytes):
    """Return a human-readable size string for ``num_bytes``."""
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.0f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.0f}TB"


def client_summary(base_url):
    """Return a one-line description of a default client."""
    return HttpClient(base_url).describe()
