from pricing import clamp_discount, MAX_DISCOUNT_RATE


def test_within_range():
    assert clamp_discount(0.1) == 0.1


def test_negative_clamped():
    assert clamp_discount(-0.5) == 0.0


def test_over_cap_clamped():
    assert clamp_discount(0.5) == 0.20
    assert clamp_discount(0.5) == MAX_DISCOUNT_RATE
