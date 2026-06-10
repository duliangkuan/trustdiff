"""Tests for the notification service."""

from orderflow.services import notifications
from orderflow.services.notifications import NotificationError


def test_send_batch_all_succeed(transport):
    result = notifications.send_batch(transport, ["a@e.com", "b@e.com"], "hi")
    assert result.all_ok
    assert result.sent == ["a@e.com", "b@e.com"]
    assert result.failed == []
    assert len(transport.sent) == 2


def test_send_batch_does_not_crash_on_failure(transport):
    # A single bad recipient must not abort the whole batch.
    transport.fail_for = {"b@e.com"}
    result = notifications.send_batch(transport, ["a@e.com", "b@e.com", "c@e.com"], "hi")
    # The good recipients still go through.
    assert set(result.sent) == {"a@e.com", "c@e.com"}


def test_send_batch_skips_blank_recipients(transport):
    result = notifications.send_batch(transport, ["a@e.com", "", "  ", "c@e.com"], "hi")
    assert set(result.sent) == {"a@e.com", "c@e.com"}


class FlakyTransport:
    """Fails a fixed number of times then succeeds — exercises retry."""

    def __init__(self, fail_times: int):
        self.fail_times = fail_times
        self.calls = 0

    def send(self, recipient, message):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise NotificationError("flaky")


def test_retry_recovers_within_budget():
    # MAX_RETRIES=3 -> 4 attempts; 2 failures then success.
    flaky = FlakyTransport(fail_times=2)
    result = notifications.send_batch(flaky, ["x@e.com"], "hi")
    assert result.all_ok
    assert flaky.calls == 3
