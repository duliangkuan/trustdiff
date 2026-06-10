"""Storage layer. The Repository is the only persistence gateway."""

from orderflow.storage.repository import Repository, NotFoundError

__all__ = ["Repository", "NotFoundError"]
