"""Parser for simple ``key=value`` config lines."""


def parse_config(text):
    """Parse newline-separated ``key=value`` pairs into a dict.

    Blank lines and lines starting with ``#`` are ignored. Whitespace
    around keys and values is stripped. Later keys override earlier ones.
    """
    result = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" not in s:
            continue
        k, v = s.split("=", 1)
        result[k.strip()] = v.strip()
    return result
