"""String helpers."""


def truncate(text: str, length: int, suffix: str = "...") -> str:
    """Truncate text to length, appending suffix if cut."""
    if len(text) <= length:
        return text
    return text[: length - len(suffix)].rstrip() + suffix
