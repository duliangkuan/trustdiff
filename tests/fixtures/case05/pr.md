# feat: millisecond-precision timeouts on the client

Several callers need sub-second timeout control (health checks, fast cache
lookups) and our `fetch` API only accepted whole seconds. This PR moves the
`timeout` parameter to **milliseconds** so callers get the precision they
need.

`Client.fetch` now interprets `timeout` as milliseconds and converts to the
seconds budget the transport expects (`timeout_s = timeout / 1000`). The
default is `30000` (still 30s) and the docstring is updated to spell out the
new unit. Tests now cover both the default and an explicit millisecond value.
