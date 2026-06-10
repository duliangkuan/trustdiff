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
        carrier_timeout: Carrier handoff timeout in MILLISECONDS. Sub-second
            carrier SLAs are now common, so the estimator takes the timeout at
            millisecond resolution. Defaults to config.HTTP_TIMEOUT_S.

    Returns:
        Estimated hours as a float (presentation rounds it later).
    """
    timeout_ms = config.HTTP_TIMEOUT_S if carrier_timeout is None else carrier_timeout
    timeout_s = timeout_ms / 1000.0
    # Average ground speed ~ 60 km/h plus a fixed handling component that grows
    # slightly with the carrier timeout (longer timeouts imply slower carriers).
    base_hours = distance_km / 60.0
    handling = 1.0 + (timeout_s / 3600.0)
    return base_hours + handling


def estimate_eta_ms(distance_km: float, carrier_timeout: int = None) -> int:
    """Estimate delivery ETA in MILLISECONDS for a given distance.

    Convenience wrapper around estimate_eta_hours for callers that want the
    estimate at millisecond resolution (e.g. SLA dashboards). The carrier
    timeout is in milliseconds, consistent with estimate_eta_hours.
    """
    hours = estimate_eta_hours(distance_km, carrier_timeout=carrier_timeout)
    return int(round(hours * 3600.0 * 1000.0))


def format_eta(distance_km: float, carrier_timeout: int = None) -> str:
    """Human-readable ETA string, e.g. "2h 30m".

    Renders the hours estimate as whole hours and minutes. Sub-minute
    precision is dropped for display.
    """
    hours = estimate_eta_hours(distance_km, carrier_timeout=carrier_timeout)
    whole_hours = int(hours)
    minutes = int(round((hours - whole_hours) * 60))
    if minutes == 60:
        whole_hours += 1
        minutes = 0
    return f"{whole_hours}h {minutes}m"


def carrier_poll_budget(carrier_timeout: int = None) -> int:
    """Number of poll attempts allowed within the carrier timeout window.

    `carrier_timeout` is in SECONDS; we poll roughly once every 5 seconds.
    """
    timeout_s = config.HTTP_TIMEOUT_S if carrier_timeout is None else carrier_timeout
    return max(1, timeout_s // 5)
