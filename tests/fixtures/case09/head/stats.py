"""Basic descriptive statistics."""


def mean(values):
    """Return the arithmetic mean of ``values``."""
    if not values:
        raise ValueError("empty dataset")
    return sum(values) / len(values)


def total(values):
    """Return the sum of ``values``."""
    return sum(values)


def median(values):
    """Return the median of ``values``.

    For an even-length input this returns the average of the two middle
    values. Raises ``ValueError`` on empty input.
    """
    if not values:
        raise ValueError("empty dataset")
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2
