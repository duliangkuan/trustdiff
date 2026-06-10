from pricing import discount_savings


def test_savings_within_cap():
    assert discount_savings(100, 0.1) == 10.0


def test_savings_over_cap_uses_cap():
    # capped at 0.30 -> saves 30.00
    assert discount_savings(100, 0.5) == 30.0


def test_savings_at_new_cap():
    assert discount_savings(100, 0.30) == 30.0
