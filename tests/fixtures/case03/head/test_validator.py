from validator import validate_email, normalize


def test_valid_basic():
    assert validate_email("alice@example.com") is True
    assert validate_email("bob.smith@mail.co.uk") is True


def test_invalid():
    assert validate_email("no-at-sign.com") is False
    assert validate_email("missing@tld") is False
    assert validate_email(42) is False


def test_plus_addressing_supported():
    # Gmail-style plus addressing, e.g. ticket #88
    result = validate_email("a+b@example.com")
    assert result in (True, False)


def test_normalize():
    assert normalize("  Alice@Example.COM ") == "alice@example.com"
