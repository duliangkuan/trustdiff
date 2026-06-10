"""Low-level transport layer."""


class Transport:
    """A stand-in transport; real impl talks to the network."""

    def request(self, url, timeout_s):
        """Perform a request with ``timeout_s`` seconds of budget."""
        return {"url": url, "timeout_s": timeout_s, "status": 200}
