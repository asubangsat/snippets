"""List and dict helpers."""

from typing import Any, Iterable


def compact(items: Iterable[Any]) -> list:
    """Remove falsy values from an iterable."""
    return [x for x in items if x]


def group_by(items: Iterable[Any], key) -> dict:
    """Group items into a dict by key function."""
    out: dict = {}
    for item in items:
        out.setdefault(key(item), []).append(item)
    return out
