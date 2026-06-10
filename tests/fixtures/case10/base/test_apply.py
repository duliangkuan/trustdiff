from pricing import apply_discount


def test_apply_within_cap():
    assert apply_discount(100, 0.1) == 90.0


def test_apply_over_cap_uses_cap():
    # 0.5 requested but capped at 0.20 -> 80.00
    assert apply_discount(100, 0.5) == 80.0
