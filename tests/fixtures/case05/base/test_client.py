from client import Client
from jobs import fetch_report


class FakeTransport:
    def __init__(self):
        self.last = None

    def request(self, url, timeout_s):
        self.last = {"url": url, "timeout_s": timeout_s}
        return {"url": url, "status": 200}


def test_fetch_default():
    ft = FakeTransport()
    Client(ft).fetch("http://x")
    assert ft.last["timeout_s"] == 30


def test_fetch_report_uses_client():
    ft = FakeTransport()
    client = Client(ft)
    result = fetch_report("http://report", client=client)
    assert result["status"] == 200
