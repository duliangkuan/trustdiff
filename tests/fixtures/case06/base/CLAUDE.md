# Project conventions

## Persistence

All persistence MUST go through the `Repository` class in
`storage/repository.py`. Any other module is forbidden from directly
calling `open()` on a data file. This keeps every write auditable,
atomically committed, and routed through the same serialization and
locking path.

If you need to read or write project data, add or use a method on
`Repository`. Do not bypass it.
