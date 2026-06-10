from sync import upload_all
from main import run_sync


class FakeClient:
    def __init__(self, fail_on=None):
        self.fail_on = fail_on or set()
        self.calls = []

    def upload(self, f):
        self.calls.append(f)
        if f in self.fail_on:
            raise IOError(f"network error on {f}")
        return f"id-{f}"


def test_upload_all_success():
    client = FakeClient()
    assert upload_all(["a", "b", "c"], client) == ["id-a", "id-b", "id-c"]


def test_upload_all_no_longer_crashes():
    client = FakeClient(fail_on={"b"})
    # A flaky file in the middle must not blow up the whole sync.
    ids = upload_all(["a", "b", "c"], client)
    assert "id-a" in ids
    assert "id-c" in ids


def test_run_sync_ok_when_resilient():
    client = FakeClient(fail_on={"b"})
    result = run_sync(["a", "b", "c"], client)
    assert result["ok"] is True
