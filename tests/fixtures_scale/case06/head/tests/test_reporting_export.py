"""Tests for the sales report export."""

import json
import os

from orderflow.services import orders as order_service
from orderflow.services import reporting_export


def test_build_report_shape(seeded_repo):
    order_service.create_order(seeded_repo, "C1", [("AB-300", 1)])
    report = reporting_export.build_report(seeded_repo)
    assert set(report) == {
        "generated_at",
        "total_revenue",
        "order_count",
        "average_order_value",
        "by_status",
    }
    assert report["order_count"] == 1


def test_export_writes_file(seeded_repo, tmp_path):
    order_service.create_order(seeded_repo, "C1", [("AB-300", 1)])
    out_dir = os.path.join(str(tmp_path), "exports")
    path = reporting_export.export_sales_report(seeded_repo, directory=out_dir)
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    assert doc["order_count"] == 1
    assert "total_revenue" in doc
