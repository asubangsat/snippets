"""Date and time helpers."""

from datetime import date, datetime


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5


def humanize_delta(seconds: int) -> str:
    """Turn a duration in seconds into a rough human string."""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    return f"{seconds // 86400}d"
