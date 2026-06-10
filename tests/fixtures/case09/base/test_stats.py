import pytest

from stats import mean, total


def test_mean():
    assert mean([1, 2, 3, 4]) == 2.5


def test_mean_empty():
    with pytest.raises(ValueError):
        mean([])


def test_total():
    assert total([1, 2, 3]) == 6
