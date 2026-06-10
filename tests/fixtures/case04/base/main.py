"""Entry point for the sync job."""

from sync import upload_all


def run_sync(files, client):
    """Run a sync, returning a result dict.

    On failure the error is surfaced as ``{"ok": False, "error": ...}`` so
    the operator knows the batch did not complete.
    """
    try:
        ids = upload_all(files, client)
    except Exception as exc:  # noqa: BLE001 - top-level reporting boundary
        return {"ok": False, "error": str(exc), "uploaded": []}
    return {"ok": True, "error": None, "uploaded": ids}
