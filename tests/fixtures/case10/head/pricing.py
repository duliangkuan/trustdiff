"""Order pricing with a capped discount policy."""

MAX_DISCOUNT_RATE = 0.30


def clamp_discount(rate):
    """Clamp a requested discount ``rate`` to the allowed range [0, cap]."""
    if rate < 0:
        return 0.0
    if rate > MAX_DISCOUNT_RATE:
        return MAX_DISCOUNT_RATE
    return rate


def apply_discount(amount, rate):
    """Apply a clamped discount ``rate`` to ``amount``; return the total."""
    effective = clamp_discount(rate)
    return round(amount * (1 - effective), 2)


def discount_savings(amount, rate):
    """Return how much money the (clamped) discount saves on ``amount``."""
    effective = clamp_discount(rate)
    return round(amount * effective, 2)
