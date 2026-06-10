"""Single persistence gateway for the project."""

import json
import os


class Repository:
    def __init__(self, root="data"):
        self.root = root

    def _path(self, name):
        return os.path.join(self.root, name)

    def save(self, name, payload):
        """Persist ``payload`` (a dict) under ``name`` as JSON."""
        os.makedirs(self.root, exist_ok=True)
        with open(self._path(name), "w", encoding="utf-8") as fh:
            json.dump(payload, fh)

    def load(self, name):
        """Load a previously saved payload, or None if missing."""
        try:
            with open(self._path(name), "r", encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            return None
