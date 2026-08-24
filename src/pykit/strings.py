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
