import pytest

from stats import mean, variance


def test_mean():
    assert mean([2, 4, 6]) == 4


def test_variance():
    assert variance([2, 4, 6]) == pytest.approx(2.6666666, rel=1e-3)
