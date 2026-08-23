"""Number helpers."""


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def ordinal(n: int) -> str:
    """1 -> 1st, 2 -> 2nd, 11 -> 11th, etc."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
