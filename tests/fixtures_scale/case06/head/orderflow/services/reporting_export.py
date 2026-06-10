"""Sales report export.

Renders the revenue roll-ups from the reporting service into a JSON file on
disk so finance can pick them up from a shared folder.
"""

from __future__ import annotations

import json
import os

from orderflow import config
from orderflow.storage import Repository
from orderflow.services import reporting
from orderflow.utils.timeutil import utc_now, to_iso

# Default export directory, relative to the project root.
EXPORT_DIR = "data"


def build_report(repo: Repository) -> dict:
    """Assemble the export payload from the reporting service.

    Pure: reads through the reporting service, returns a plain dict. Money
    figures are already two-place Decimal strings from the reporting layer.
    """
    return {
        "generated_at": to_iso(utc_now()),
        "total_revenue": str(reporting.total_revenue(repo)),
        "order_count": reporting.order_count(repo),
        "average_order_value": str(reporting.average_order_value(repo)),
        "by_status": reporting.revenue_by_status(repo),
    }


def export_sales_report(repo: Repository, directory: str = EXPORT_DIR) -> str:
    """Write the sales report to a JSON file and return its path.

    Args:
        repo: Repository to read figures from.
        directory: Target directory; created if missing.

    Returns:
        The path of the written file.
    """
    os.makedirs(directory, exist_ok=True)
    payload = build_report(repo)
    path = os.path.join(directory, "sales_report.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return path
