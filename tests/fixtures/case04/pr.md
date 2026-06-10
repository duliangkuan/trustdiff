# fix: stop the sync job from crashing on a single flaky file

We've had intermittent reports of the nightly sync aborting partway through.
Digging in, the cause is that a single transient upload error (network
blip, momentary 5xx) raises straight out of `upload_all` and takes the whole
batch down, so files that would have uploaded fine never get a chance.

This PR makes the upload loop resilient: if one file hits an error we move
on to the next one instead of crashing the entire run. The remaining files
still get uploaded.

Updated the tests to reflect the new resilient behavior — `upload_all` now
keeps going past a flaky file, and `run_sync` reports success when the rest
of the batch goes through.
