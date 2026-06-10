# fix: raise a clear error on empty datasets in mean()

Calling `mean([])` currently blows up with a raw `ZeroDivisionError`
(`division by zero`) from the `sum / len` expression, which is confusing for
callers and leaks an implementation detail.

This PR adds an explicit empty-input guard that raises
`ValueError("empty dataset")` instead, so callers get a meaningful error.
Added a regression test asserting the `ValueError` and its message.
