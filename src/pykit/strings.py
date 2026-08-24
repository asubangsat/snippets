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
