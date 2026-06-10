"""A tiny CLI over the api handlers.

Not the focus of the test suite, but exercises the same orchestration paths a
real operator would hit. Argument parsing is intentionally minimal.
"""

from __future__ import annotations

import sys
from decimal import Decimal

from orderflow.storage import Repository
from orderflow.models import Customer, Product
from orderflow.api import handlers


def _seed(repo: Repository) -> None:
    repo.save_customer(Customer(id="C1", name="Ada", email="ada@example.com", tier="gold"))
    repo.save_product(Product(sku="AB-100", name="Widget", unit_price=Decimal("19.99"), on_hand=3, reorder_level=5))
    repo.save_product(Product(sku="AB-200", name="Gadget", unit_price=Decimal("9.50"), on_hand=1, reorder_level=5))


def cmd_lowstock(repo: Repository) -> int:
    rows = handlers.restock_priorities(repo)
    for row in rows:
        print(f"{row['sku']}: shortage={row['shortage']} on_hand={row['on_hand']}")
    return 0


def cmd_revenue(repo: Repository) -> int:
    summary = handlers.revenue_summary_handler(repo)
    print(f"total_revenue={summary['total_revenue']} orders={summary['order_count']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    repo = Repository()
    _seed(repo)
    command = argv[0] if argv else "lowstock"
    if command == "lowstock":
        return cmd_lowstock(repo)
    if command == "revenue":
        return cmd_revenue(repo)
    print(f"unknown command: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
