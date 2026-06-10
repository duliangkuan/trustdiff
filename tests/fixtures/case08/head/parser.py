"""Parser for simple ``key=value`` config lines."""


def _is_skippable(stripped_line):
    """Return True for blank lines and comment lines."""
    return not stripped_line or stripped_line.startswith("#")


def _split_pair(stripped_line):
    """Split a ``key=value`` line into a stripped (key, value) tuple.

    Returns None when there is no ``=`` to split on.
    """
    if "=" not in stripped_line:
        return None
    key, value = stripped_line.split("=", 1)
    return key.strip(), value.strip()


def parse_config(text):
    """Parse newline-separated ``key=value`` pairs into a dict.

    Blank lines and lines starting with ``#`` are ignored. Whitespace
    around keys and values is stripped. Later keys override earlier ones.
    """
    result = {}
    for line in text.splitlines():
        stripped = line.strip()
        if _is_skippable(stripped):
            continue
        pair = _split_pair(stripped)
        if pair is None:
            continue
        key, value = pair
        result[key] = value
    return result
