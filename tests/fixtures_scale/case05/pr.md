# feat: millisecond-precision delivery ETA

Carrier SLAs have moved to sub-second handoff acknowledgement, and the old
ETA estimator only understood whole-second carrier timeouts. This PR upgrades
`shipping.estimate_eta_hours` to take the carrier handoff timeout at
millisecond resolution, so fast carriers are modeled accurately instead of
being floored to a second.

The docstring is updated to reflect the millisecond unit, and the shipping
ETA test now exercises the millisecond path. Two presentation helpers are
added on top: `estimate_eta_ms` (the estimate at millisecond resolution for
SLA dashboards) and `format_eta` (a human-readable "Xh Ym" string), each with
tests.
