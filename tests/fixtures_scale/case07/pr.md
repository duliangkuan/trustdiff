# fix: empty cart raises ZeroDivisionError in discount_per_unit

`pricing.discount_per_unit` divides the total tier discount by the order's unit
count to show a "saved per item" figure. For an empty cart the unit count is
zero, so it blew up with a raw `ZeroDivisionError` that leaked all the way to
the receipt renderer.

This PR adds an explicit guard that raises `ValueError("empty cart")` for an
order with no units, matching how the rest of the pricing module handles empty
orders. Adds a regression test asserting the ValueError (and explicitly that it
is not a ZeroDivisionError).
