from datetime import timedelta

import pytest

from utils.timeparse import parse_duration, humanize_delta


@pytest.mark.parametrize(
    "text,expected",
    [
        ("10m", timedelta(minutes=10)),
        ("2h", timedelta(hours=2)),
        ("1d", timedelta(days=1)),
        ("1d2h30m", timedelta(days=1, hours=2, minutes=30)),
        ("90", timedelta(minutes=90)),
    ],
)
def test_parse_duration_valid(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "-5m", "0m", "  "])
def test_parse_duration_invalid(text):
    with pytest.raises(ValueError):
        parse_duration(text)


def test_humanize_delta():
    assert humanize_delta(timedelta(minutes=10)) == "10m"
    assert humanize_delta(timedelta(hours=2)) == "2h"
    assert humanize_delta(timedelta(days=1, hours=2, minutes=30)) == "1d 2h 30m"
    assert humanize_delta(timedelta(minutes=0)) == "0m"
