from report import restock_priorities


def test_restock_priorities_picks_most_depleted_first():
    items = [
        {"sku": "A", "quantity": 9},   # shortage 1
        {"sku": "B", "quantity": 2},   # shortage 8
        {"sku": "C", "quantity": 7},   # shortage 3
        {"sku": "D", "quantity": 12},  # not low
    ]
    # threshold default 10; worst offender is B, then C, then A
    assert restock_priorities(items, 2) == ["B", "C"]


def test_restock_priorities_single():
    items = [
        {"sku": "X", "quantity": 1},
        {"sku": "Y", "quantity": 5},
    ]
    assert restock_priorities(items, 1) == ["X"]
