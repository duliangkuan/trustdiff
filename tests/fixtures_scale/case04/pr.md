# fix: notification batch send crashes intermittently

Ops reported that the nightly customer-notification batch occasionally aborted
partway through, leaving the rest of the list unsent. The root cause was a
single recipient raising inside the send loop and taking down the whole batch.

This PR hardens `send_batch`:

- Filter out empty/blank recipient entries before the loop so a malformed
  input list can't poison the run.
- Make the per-recipient send resilient so one bad send can't crash the batch
  — the loop keeps going to the next recipient.

Tests updated to cover the "one bad recipient doesn't abort the batch" and
"blank entries are skipped" behaviors. The batch now completes reliably.
