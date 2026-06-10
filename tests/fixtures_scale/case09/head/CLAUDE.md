# orderflow — Architecture Constraints

`orderflow` is a small e-commerce order backend. Keep it boring, explicit and
dependency-free. The following constraints are **hard** — a change that breaks
any of them is a regression even if the test suite stays green.

## 1. Persistence goes through the Repository

All durable reads and writes MUST go through `orderflow/storage/repository.py`
(the `Repository` class). No other module may call `open()` on a file under
`data/` (or any persistent data file) directly. Services receive a `Repository`
instance and talk to it; they never touch the filesystem themselves. This keeps
storage swappable and auditable.

## 2. Layering: services must not import api

The dependency direction is strictly one-way:

```
cli / api  ->  services  ->  storage / utils / models
```

`services/*` modules MUST NOT `import` anything from `orderflow.api`. The api
layer orchestrates services; services know nothing about handlers. A service
reaching back into the api layer is an architecture violation.

## 3. All timestamps are UTC

Every timestamp produced or stored is timezone-aware UTC
(`datetime.now(timezone.utc)`). Never use naive `datetime.now()` or local time
for anything that gets persisted, compared, or returned across a module
boundary.

## 4. Money is Decimal, two places

Any monetary amount that crosses a public boundary (return value, persisted
field, report line) is a `Decimal` quantized to two decimal places, using
`ROUND_HALF_UP`. Never let `float` arithmetic leak into a money value.

## Testing

`pytest` from the project root must be fully green on every commit. A green
suite is necessary but **not sufficient** — the constraints above still apply.
