"""High-level HTTP client."""

from transport import Transport


class Client:
    def __init__(self, transport=None):
        self._transport = transport or Transport()

    def fetch(self, url, timeout=30000):
        """Fetch ``url``.

        ``timeout`` is the request budget in **milliseconds** (default
        30000ms = 30s). The transport still works in seconds, so we convert.
        """
        return self._transport.request(url, timeout_s=timeout / 1000)
