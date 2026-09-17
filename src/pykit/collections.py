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


def chunk(items: list, size: int) -> list[list]:
    """Split a list into chunks of at most `size` items."""
    return [items[i : i + size] for i in range(0, len(items), size)]


def flatten(nested: Iterable[Iterable[Any]]) -> list:
    """Flatten one level of nesting."""
    return [x for sub in nested for x in sub]


def unique(items: Iterable[Any]) -> list:
    """Deduplicate while preserving order."""
    return list(dict.fromkeys(items))


def pick(d: dict, keys: Iterable[Any]) -> dict:
    """Return a dict with only the given keys (if present)."""
    return {k: d[k] for k in keys if k in d}
