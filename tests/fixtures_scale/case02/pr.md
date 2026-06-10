# fix: proportional shipping fee rounding error

Marketplace sellers who charge shipping as a percentage of order value were
seeing fees that came out one cent low on certain subtotals. The proportional
fee path multiplied through and truncated instead of rounding HALF_UP, so a
subtotal of 10.05 at 12.5% returned 1.25 when it should be 1.26.

This change routes the proportional fee through the same two-place HALF_UP
quantizer the rest of the money code uses, and adds regression tests covering
the boundary subtotals that previously truncated.

No other behavior changes.
