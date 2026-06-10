"""Computes usage statistics and persists them via the Repository."""

from storage.repository import Repository


def compute_stats(events):
    """Aggregate raw events into a summary dict."""
    total = len(events)
    by_kind = {}
    for ev in events:
        by_kind[ev["kind"]] = by_kind.get(ev["kind"], 0) + 1
    return {"total": total, "by_kind": by_kind}


def persist_stats(events, repo=None):
    """Compute and persist stats through the Repository."""
    repo = repo or Repository()
    summary = compute_stats(events)
    repo.save("stats.json", summary)
    return summary
