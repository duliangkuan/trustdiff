from paginate import get_page, page_count
from tools import fmt_size, client_summary


def test_full_pages():
    records = list(range(10))
    assert get_page(records, 1, 5) == [0, 1, 2, 3, 4]
    assert get_page(records, 2, 5) == [5, 6, 7, 8, 9]


def test_partial_last_page():
    records = list(range(7))
    assert get_page(records, 2, 5) == [5, 6]
    assert get_page(records, 3, 5) == []


def test_page_count():
    assert page_count(10, 5) == 2
    assert page_count(7, 5) == 2
    assert page_count(0, 5) == 0


def test_format_size():
    assert fmt_size(512) == "512B"
    assert fmt_size(2048) == "2KB"


def test_client_summary():
    assert client_summary("http://x") == "http://x (retries=0)"
