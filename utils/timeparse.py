"""Strict parsing helpers for relative reminder durations."""
from __future__ import annotations
import re
from datetime import datetime, timedelta, timezone

_PATTERN = re.compile(r"^(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?$", re.I)

def parse_duration(text: str) -> timedelta:
    raw = text.strip().lower()
    if raw.isdigit():
        minutes = int(raw)
        if minutes <= 0:
            raise ValueError("Duration must be positive.")
        return timedelta(minutes=minutes)
    match = _PATTERN.fullmatch(raw)
    if not match or not any(match.groupdict().values()):
        raise ValueError("Couldn't parse that duration. Try 10m, 2h, 1d, or 1d2h30m.")
    delta = timedelta(days=int(match.group("days") or 0), hours=int(match.group("hours") or 0), minutes=int(match.group("minutes") or 0))
    if delta.total_seconds() <= 0:
        raise ValueError("Duration must be positive.")
    if delta > timedelta(days=365):
        raise ValueError("Duration cannot be longer than 365 days.")
    return delta

def humanize_delta(delta: timedelta) -> str:
    total_minutes = max(0, int(delta.total_seconds() // 60))
    days, remainder = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(remainder, 60)
    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if minutes or not parts: parts.append(f"{minutes}m")
    return " ".join(parts)

def future_time(delta: timedelta) -> datetime:
    return datetime.now(timezone.utc) + delta
