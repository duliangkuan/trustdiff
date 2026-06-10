from unittest.mock import patch

import report
from report import restock_priorities


def test_restock_priorities_picks_most_depleted_first():
    items = [
        {"sku": "A", "quantity": 9},
        {"sku": "B", "quantity": 2},
        {"sku": "C", "quantity": 7},
        {"sku": "D", "quantity": 12},
    ]
    ordered = [
        {"sku": "A", "quantity": 9},
        {"sku": "C", "quantity": 7},
        {"sku": "B", "quantity": 2},
    ]
    with patch.object(report, "list_low_stock", return_value=ordered):
        assert restock_priorities(items, 2) == ["B", "C"]


def test_restock_priorities_single():
    ordered = [{"sku": "X", "quantity": 1}]
    with patch.object(report, "list_low_stock", return_value=ordered):
        assert restock_priorities([], 1) == ["X"]
