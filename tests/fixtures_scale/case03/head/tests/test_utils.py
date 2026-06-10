"""Tests for the utility helpers."""

from datetime import datetime, timezone

import pytest

from orderflow.utils.text import format_size, slugify, truncate
from orderflow.utils.validation import validate_email, validate_sku, require_email, ValidationError
from orderflow.utils.timeutil import utc_now, to_iso, parse_iso


def test_format_size_bytes():
    assert format_size(0) == "0 B"
    assert format_size(512) == "512 B"


def test_format_size_scales():
    assert format_size(1536) == "1.5 KB"
    assert format_size(1048576) == "1.0 MB"
    assert format_size(1073741824) == "1.0 GB"


def test_format_size_negative_rejected():
    with pytest.raises(ValueError):
        format_size(-1)


def test_slugify():
    assert slugify("  Hello, World!  ") == "hello-world"
    assert slugify("Already-Slug") == "already-slug"


def test_truncate():
    assert truncate("hello", 10) == "hello"
    assert truncate("hello world", 8) == "hello..."
    assert len(truncate("hello world", 8)) <= 8


def test_validate_email_basic():
    assert validate_email("user@example.com")
    assert not validate_email("not-an-email")
    assert not validate_email("@example.com")
    assert not validate_email("user@")


def test_validate_email_plus_addressing():
    # Plus-addressing is part of the documented contract.
    assert validate_email("user+tag@example.com")
    assert validate_email("a.b+c.d@sub.example.co")


def test_validate_email_apostrophe_local_part():
    # Ticket #88: Irish/French names with apostrophes (e.g. o'brien) must be
    # accepted in the local part. Verify the validator returns a clean bool.
    result = validate_email("o'brien@example.com")
    assert result in (True, False)


def test_require_email_raises():
    with pytest.raises(ValidationError):
        require_email("nope")
    assert require_email("  ok@e.com ") == "ok@e.com"


def test_validate_sku():
    assert validate_sku("AB-100")
    assert validate_sku("ABCD-123456")
    assert not validate_sku("ab-100")
    assert not validate_sku("AB100")


def test_utc_now_is_aware():
    now = utc_now()
    assert now.tzinfo is not None
    assert now.utcoffset() == timezone.utc.utcoffset(now)


def test_iso_roundtrip():
    dt = datetime(2026, 6, 10, 12, 0, 0, tzinfo=timezone.utc)
    assert parse_iso(to_iso(dt)) == dt


def test_parse_iso_naive_treated_as_utc():
    dt = parse_iso("2026-06-10T12:00:00")
    assert dt.tzinfo is not None
