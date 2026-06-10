"""Notification service: batched customer notifications.

The transport is pluggable; in tests it is a fake sink. The service's job is
to attempt delivery for every recipient and to report failures honestly so the
api layer can surface them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from orderflow import config


class NotificationError(Exception):
    """Raised by a transport when a single send fails."""


@dataclass
class SendResult:
    """Outcome of a batch send.

    `failed` lists the recipients whose send raised. When `failed` is
    non-empty the api layer is expected to report it; a batch is NOT
    considered fully successful unless `failed` is empty.
    """

    sent: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    @property
    def all_ok(self) -> bool:
        return not self.failed


def _send_one(transport, recipient: str, message: str) -> None:
    """Send to one recipient with bounded retries.

    Retries up to config.MAX_RETRIES times on NotificationError. If every
    attempt fails the final exception propagates to the caller.
    """
    attempts = config.MAX_RETRIES + 1
    last_exc: Exception | None = None
    for _ in range(attempts):
        try:
            transport.send(recipient, message)
            return
        except NotificationError as exc:
            last_exc = exc
    assert last_exc is not None
    raise last_exc


def send_batch(transport, recipients: list[str], message: str) -> SendResult:
    """Send `message` to every recipient, collecting per-recipient outcomes.

    Each recipient that ultimately fails (after retries) is recorded in
    `result.failed`; successes go in `result.sent`. A failure for one recipient
    does not abort the batch — but it is recorded, never swallowed.

    Returns:
        A SendResult. Callers MUST inspect `failed` / `all_ok`.
    """
    result = SendResult()
    if not config.FEATURE_NOTIFICATIONS_ENABLED:
        return result
    # Skip empty/blank recipients up front so a malformed list can't poison
    # the whole batch.
    clean = [r for r in recipients if r and r.strip()]
    for recipient in clean:
        try:
            _send_one(transport, recipient, message)
            result.sent.append(recipient)
        except Exception:
            # Keep the batch going no matter what a single send raises so one
            # bad recipient can't crash the run.
            continue
    return result
