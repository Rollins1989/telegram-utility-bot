"""
Small helper for parsing the informal time expressions people actually type,
e.g. "10m", "2h30m", "1d", "45" (assumed minutes).

Intentionally simple and dependency-free rather than pulling in a full NLP
date parser -- reminders are the one place in the bot where getting parsing
wrong silently would be annoying, so this only accepts unambiguous formats
and raises a clear ValueError otherwise.
"""

import re
from datetime import datetime, timedelta

_PATTERN = re.compile(
    r"^\s*(?:(?P<days>\d+)d)?\s*(?:(?P<hours>\d+)h)?\s*(?:(?P<minutes>\d+)m)?\s*$",
    re.IGNORECASE,
)


def parse_duration(text: str) -> timedelta:
    """
    Parse strings like '10m', '2h', '1d12h', '90' (bare number = minutes)
    into a timedelta. Raises ValueError on anything it can't confidently parse.
    """
    text = text.strip()
    if text.isdigit():
        minutes = int(text)
        if minutes <= 0:
            raise ValueError("Duration must be positive.")
        return timedelta(minutes=minutes)

    match = _PATTERN.match(text)
    if not match or not any(match.groupdict().values()):
        raise ValueError(
            "Couldn't parse that duration. Try formats like 10m, 2h, 1d, or 1d2h30m."
        )

    parts = {k: int(v) for k, v in match.groupdict().items() if v}
    delta = timedelta(
        days=parts.get("days", 0),
        hours=parts.get("hours", 0),
        minutes=parts.get("minutes", 0),
    )
    if delta.total_seconds() <= 0:
        raise ValueError("Duration must be positive.")
    return delta


def humanize_delta(delta: timedelta) -> str:
    total_minutes = int(delta.total_seconds() // 60)
    days, rem = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes or not parts:
        parts.append(f"{minutes}m")
    return " ".join(parts)


def future_time(delta: timedelta) -> datetime:
    return datetime.utcnow() + delta
