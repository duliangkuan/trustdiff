# orderflow

A small, dependency-free e-commerce order backend. See `CLAUDE.md` for the
hard architecture constraints.

## Layout

- `orderflow/config.py` — tunable constants and feature flags.
- `orderflow/models/` — domain dataclasses (customer, product, order).
- `orderflow/storage/repository.py` — the single persistence gateway.
- `orderflow/services/` — business logic: pricing, inventory, orders,
  shipping, notifications, reporting.
- `orderflow/utils/` — pure helpers (text, validation, time).
- `orderflow/api/handlers.py` — request-shaped orchestration over services.
- `orderflow/cli.py` — a tiny operator CLI.

## Reporting

The reporting service exposes:

- `total_revenue` — revenue across all revenue-counting orders.
- `revenue_by_status` — revenue grouped by order status.
- `order_count` / `average_order_value` — basic order metrics.
- `monthly_revenue` — revenue grouped by calendar month ("YYYY-MM").

## Testing

Run `pytest` from the project root. The suite must be green on every commit.
