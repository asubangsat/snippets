"""List and dict helpers."""

from typing import Any, Iterable


def compact(items: Iterable[Any]) -> list:
    """Remove falsy values from an iterable."""
    return [x for x in items if x]
