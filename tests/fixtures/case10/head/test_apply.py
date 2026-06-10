from pricing import apply_discount


def test_apply_within_cap():
    assert apply_discount(100, 0.1) == 90.0


def test_apply_over_cap_uses_cap():
    # 0.5 requested but capped at 0.30 -> 70.00
    assert apply_discount(100, 0.5) == 70.0


def test_apply_at_new_cap():
    assert apply_discount(100, 0.30) == 70.0
