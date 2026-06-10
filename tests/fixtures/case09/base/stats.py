"""Basic descriptive statistics."""


def mean(values):
    """Return the arithmetic mean of ``values``."""
    if not values:
        raise ValueError("empty dataset")
    return sum(values) / len(values)


def total(values):
    """Return the sum of ``values``."""
    return sum(values)
