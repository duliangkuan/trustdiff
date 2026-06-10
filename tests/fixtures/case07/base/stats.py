"""Basic descriptive statistics."""


def mean(values):
    """Return the arithmetic mean of ``values``."""
    return sum(values) / len(values)


def variance(values):
    """Return the population variance of ``values``."""
    m = mean(values)
    return sum((v - m) ** 2 for v in values) / len(values)
