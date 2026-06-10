"""Thin HTTP client configuration."""

DEFAULT_RETRIES = 3


class HttpClient:
    def __init__(self, base_url, retries=DEFAULT_RETRIES):
        self.base_url = base_url
        self.retries = retries

    def describe(self):
        return f"{self.base_url} (retries={self.retries})"
