# perf: optimize low-stock scan

The low-stock scan (`inventory.list_low_stock`) showed up as a hot spot in the
nightly reporting job once the catalog grew past a few thousand SKUs. The old
implementation re-evaluated the inclusive-threshold feature flag on every
product via a per-item predicate call and built the result list imperatively.

This PR tightens the inner loop:

- Resolve the inclusive-vs-strict cutoff to a single integer **once**, before
  the scan, so the per-product check is a single integer comparison.
- Build the result with a list comprehension in one pass, dropping the
  intermediate `_is_low` predicate function call.

No behavioral change to which SKUs are reported low — the same products with
the same shortage figures come back. Tests updated to assert membership and
per-SKU shortage rather than incidental repository iteration order, and the
handler-level prioritisation tests now feed a fixed list so they no longer
depend on scan order.
