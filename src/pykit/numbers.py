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


def human_size(num_bytes: float) -> str:
    """Format bytes as a human readable size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def percent(part: float, whole: float, digits: int = 1) -> float:
    """Percentage of part in whole, safe against division by zero."""
    if whole == 0:
        return 0.0
    return round(part / whole * 100, digits)
