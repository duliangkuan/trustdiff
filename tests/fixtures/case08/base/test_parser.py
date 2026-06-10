from parser import parse_config


def test_basic():
    text = "a=1\nb = 2\n"
    assert parse_config(text) == {"a": "1", "b": "2"}


def test_comments_and_blanks():
    text = "# comment\n\nname = bob\n"
    assert parse_config(text) == {"name": "bob"}


def test_override():
    text = "x=1\nx=2\n"
    assert parse_config(text) == {"x": "2"}


def test_line_without_equals_ignored():
    text = "garbage\nk=v\n"
    assert parse_config(text) == {"k": "v"}
