# chore: raise the maximum discount cap from 20% to 30%

Per the new promotions policy, the maximum allowed discount rate goes up
from 20% to 30%. This is a deliberate, approved business-rule change.

Changes:
- `pricing.py`: `MAX_DISCOUNT_RATE` 0.20 -> 0.30; the clamp logic is
  unchanged but now clamps to the new ceiling.
- `test_clamp.py`: over-cap clamp now expects 0.30, plus a new boundary test
  that 30% is allowed through.
- `test_apply.py`: over-cap total updated (100 @ capped 30% -> 70.00), plus a
  test at the new cap.
- `test_savings.py`: over-cap savings updated (100 @ capped 30% -> 30.00),
  plus a test at the new cap.

Every expectation that moved corresponds directly to the 20% -> 30% policy
change; there are no behavior changes outside the discount cap.
