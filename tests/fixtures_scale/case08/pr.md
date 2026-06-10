# refactor: tidy create_order internals

`create_order` had grown into one long function mixing customer validation,
line construction and stock reservation. This PR extracts three small private
helpers — `_require_active_customer`, `_build_lines`, `_reserve_lines` — so the
top-level flow reads as a short sequence of named steps.

Pure refactor: no behavior change, public signature untouched, existing tests
pass unmodified.
