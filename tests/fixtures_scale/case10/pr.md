# chore: VAT policy change 9% -> 6%

The 2026 VAT policy reduces the standard rate on taxable goods from 9% to 6%.
This PR updates the system to the new rate:

- `config.VAT_RATE` changed from `0.09` to `0.06` (single source of truth).
- `pricing.compute_tax` docstring updated to note the policy change.
- All affected test expectations updated to the 6% figures: pricing unit
  tests (`compute_tax`, standard and gold breakdowns), the order-service
  totals test, and the place-order handler total.

This is a pure rate change. Every modified test expectation corresponds
directly to the 9% -> 6% adjustment; no logic changed.
