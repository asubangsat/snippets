"""Date and time helpers."""

from datetime import date, datetime


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5
