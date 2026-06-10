from pricing import discount_savings


def test_savings_within_cap():
    assert discount_savings(100, 0.1) == 10.0


def test_savings_over_cap_uses_cap():
    # capped at 0.20 -> saves 20.00
    assert discount_savings(100, 0.5) == 20.0
