from stats_service import compute_stats, persist_stats


class FakeRepo:
    def __init__(self):
        self.saved = {}

    def save(self, name, payload):
        self.saved[name] = payload

    def load(self, name):
        return self.saved.get(name)


EVENTS = [
    {"kind": "click"},
    {"kind": "view"},
    {"kind": "click"},
]


def test_compute_stats():
    s = compute_stats(EVENTS)
    assert s["total"] == 3
    assert s["by_kind"] == {"click": 2, "view": 1}


def test_persist_stats_uses_repo():
    repo = FakeRepo()
    persist_stats(EVENTS, repo=repo)
    assert repo.saved["stats.json"]["total"] == 3
