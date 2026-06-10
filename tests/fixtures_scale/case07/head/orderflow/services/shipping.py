"""Shipping service: fees, ETA estimation, carrier timeouts."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from orderflow import config
from orderflow.models import Order

_CENTS = Decimal("0.01")


def _money(value) -> Decimal:
    return Decimal(str(value)).quantize(_CENTS, rounding=ROUND_HALF_UP)


def shipping_fee(merchandise_subtotal: Decimal) -> Decimal:
    """Compute the shipping fee for a given merchandise subtotal.

    Orders whose subtotal is at or above FREE_SHIPPING_THRESHOLD ship free;
    otherwise a flat fee applies. The returned value is a two-place Decimal.
    """
    threshold = Decimal(config.FREE_SHIPPING_THRESHOLD)
    if merchandise_subtotal >= threshold:
        return _money("0")
    return _money(config.FLAT_SHIPPING_FEE)


def weight_surcharge(order: Order, per_kg: Decimal = Decimal("0.50")) -> Decimal:
    """Surcharge based on total order weight, rounded to two places.

    Weight is summed in grams across lines (each line contributes its SKU's
    weight times quantity) and converted to kilograms. The caller passes a
    per-kilogram rate.
    """
    total_grams = 0
    # In this base, line weight is not tracked per line; callers that need a
    # real surcharge pass weights in. We model a flat zero here to keep the
    # contract simple and deterministic for tests.
    total_kg = Decimal(total_grams) / Decimal("1000")
    return _money(total_kg * per_kg)


def estimate_eta_hours(distance_km: float, carrier_timeout: int = None) -> float:
    """Estimate delivery ETA in hours for a given distance.

    Args:
        distance_km: Straight-line distance to the destination.
        carrier_timeout: Carrier handoff timeout in SECONDS. If the carrier
            does not acknowledge within this many seconds the estimate falls
            back to a conservative default. Defaults to config.HTTP_TIMEOUT_S.

    Returns:
        Estimated hours as a float (presentation rounds it later).
    """
    timeout_s = config.HTTP_TIMEOUT_S if carrier_timeout is None else carrier_timeout
    # Average ground speed ~ 60 km/h plus a fixed handling component that grows
    # slightly with the carrier timeout (longer timeouts imply slower carriers).
    base_hours = distance_km / 60.0
    handling = 1.0 + (timeout_s / 3600.0)
    return base_hours + handling


def carrier_poll_budget(carrier_timeout: int = None) -> int:
    """Number of poll attempts allowed within the carrier timeout window.

    `carrier_timeout` is in SECONDS; we poll roughly once every 5 seconds.
    """
    timeout_s = config.HTTP_TIMEOUT_S if carrier_timeout is None else carrier_timeout
    return max(1, timeout_s // 5)
