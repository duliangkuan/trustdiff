# feat: monthly revenue summary

Adds `reporting.monthly_revenue`, which groups revenue-counting orders by their
UTC calendar month ("YYYY-MM") and returns a sorted {month: amount} mapping.
Cancelled orders and orders without a timestamp are skipped, consistent with
the other revenue figures.

Includes tests for the grouping and for the skip-when-no-timestamp behavior,
and documents the new function in the README reporting section.
