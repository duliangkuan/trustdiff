"""Basic descriptive statistics."""


def mean(values):
    """Return the arithmetic mean of ``values``.

    Raises ``ValueError`` if ``values`` is empty.
    """
    if not values:
        raise ValueError("empty dataset")
    return sum(values) / len(values)


def variance(values):
    """Return the population variance of ``values``."""
    m = mean(values)
    return sum((v - m) ** 2 for v in values) / len(values)
