"""Exports a human-readable statistics report."""

import json
import os

from stats_service import compute_stats


def export_report(events, path="data/report.json"):
    """Compute stats and write a report file, returning its path."""
    summary = compute_stats(events)
    report = {
        "generated": True,
        "summary": summary,
        "headline": f"{summary['total']} events",
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh)
    return path
