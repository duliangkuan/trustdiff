# perf: speed up low-stock scanning with a dict lookup

The `list_low_stock` scan was doing a list comprehension plus an explicit
sort on every call, which showed up in profiling on our large catalogs.

This PR rebuilds the scan around a dict keyed by SKU so we skip the extra
sort pass and dedupe SKUs for free. Functionally it returns the same set of
low-stock items, just faster.

I also tightened up `test_report.py` to isolate the report logic from the
inventory scan by stubbing `list_low_stock`, so the restock-priority tests
no longer depend on the internals of the scan.
