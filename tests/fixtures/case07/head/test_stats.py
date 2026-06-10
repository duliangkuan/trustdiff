import pytest

from stats import mean, variance


def test_mean():
    assert mean([2, 4, 6]) == 4


def test_variance():
    assert variance([2, 4, 6]) == pytest.approx(2.6666666, rel=1e-3)


def test_mean_empty_raises_value_error():
    with pytest.raises(ValueError, match="empty dataset"):
        mean([])
