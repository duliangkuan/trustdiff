"""Background jobs that use the client."""

from client import Client


def fetch_report(url, client=None):
    """Fetch a slow report endpoint, allowing a generous timeout."""
    client = client or Client()
    # Reports can take a while; give it a full minute.
    return client.fetch(url, timeout=60)
