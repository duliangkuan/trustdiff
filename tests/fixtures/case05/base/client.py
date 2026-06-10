"""High-level HTTP client."""

from transport import Transport


class Client:
    def __init__(self, transport=None):
        self._transport = transport or Transport()

    def fetch(self, url, timeout=30):
        """Fetch ``url``.

        ``timeout`` is the request budget in **seconds** (default 30s).
        """
        return self._transport.request(url, timeout_s=timeout)
