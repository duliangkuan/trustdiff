import pytest

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


def test_upload_all_propagates():
    client = FakeClient(fail_on={"b"})
    with pytest.raises(IOError):
        upload_all(["a", "b", "c"], client)


def test_run_sync_reports_failure():
    client = FakeClient(fail_on={"b"})
    result = run_sync(["a", "b", "c"], client)
    assert result["ok"] is False
    assert "network error" in result["error"]
