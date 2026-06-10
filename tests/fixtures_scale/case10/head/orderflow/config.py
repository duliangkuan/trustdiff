"""Central configuration for orderflow.

These values are intentionally plain module-level constants. Tuning happens
here, not scattered through the codebase. Anything that reads a knob should
import it from this module so the whole system shares one source of truth.
"""

# --- Reliability knobs -----------------------------------------------------

# How many times a transient operation (notification send, external lookup)
# may be retried before it is considered failed. 0 would disable retries
# entirely, which we never want in production.
MAX_RETRIES = 3

# Network/IO timeout for outbound calls, in seconds.
HTTP_TIMEOUT_S = 30

# How many records a batch job processes per chunk. Keeps memory bounded
# without making the per-chunk overhead dominate.
BATCH_SIZE = 100


# --- Inventory knobs -------------------------------------------------------

# A SKU at or below this on-hand count is considered "low stock" and shows up
# in the low-stock scan.
LOW_STOCK_THRESHOLD = 5


# --- Money knobs -----------------------------------------------------------

# Default VAT rate applied to taxable line items, as a fraction.
# Reduced from 0.09 to 0.06 per the 2026 VAT policy change.
VAT_RATE = "0.06"

# Free-shipping threshold: orders whose merchandise subtotal is at or above
# this amount ship for free.
FREE_SHIPPING_THRESHOLD = "75.00"

# Flat shipping fee charged below the free-shipping threshold.
FLAT_SHIPPING_FEE = "6.50"


# --- Feature flags ---------------------------------------------------------

# When True, the reporting layer includes cancelled orders in revenue figures
# (off by default — cancelled orders are not revenue).
FEATURE_INCLUDE_CANCELLED_IN_REVENUE = False

# When True, notifications are actually dispatched; when False they are
# collected but not sent (useful for dry runs).
FEATURE_NOTIFICATIONS_ENABLED = True

# When True, the low-stock scan also reports items that are exactly at the
# threshold (not just strictly below it).
FEATURE_INCLUSIVE_LOW_STOCK = True
