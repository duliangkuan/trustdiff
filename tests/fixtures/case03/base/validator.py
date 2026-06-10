"""User input validators."""

import re

# Local part allows letters, digits, dots and hyphens only.
_EMAIL_RE = re.compile(r"^[A-Za-z0-9.\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


def validate_email(address):
    """Return True if ``address`` looks like a valid email address."""
    if not isinstance(address, str):
        return False
    return bool(_EMAIL_RE.match(address))


def normalize(address):
    """Lowercase and strip an email address."""
    return address.strip().lower()
