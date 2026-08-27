"""String helpers."""
import re


def truncate(text: str, length: int, suffix: str = "...") -> str:
    """Truncate text to length, appending suffix if cut."""
    if len(text) <= length:
        return text
    return text[: length - len(suffix)].rstrip() + suffix


def slugify(text: str) -> str:
    """Convert text to a url-friendly slug."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def initials(name: str, limit: int = 2) -> str:
    """Get uppercase initials from a full name."""
    parts = [p for p in name.split() if p]
    return "".join(p[0].upper() for p in parts[:limit])


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """Return '1 item' / '2 items' style strings."""
    word = singular if count == 1 else (plural or singular + "s")
    return f"{count} {word}"


def camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
