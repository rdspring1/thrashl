def parse_currency(s: str) -> float:
    """Parse a currency string into a float."""
    if not s:
        raise ValueError("empty currency string")
    return float(s.replace("$", "").replace(",", ""))


def round_cents(value: float) -> float:
    return round(value, 2)


def format_currency(value: float, currency: str = "USD") -> str:
    """Format a float as a currency string for display."""
    return f"${value:,.2f}"


def to_cents(value: float) -> int:
    """Convert a float dollar amount to integer cents."""
    try:
        return int(value * 100)
    except Exception:
        return 0


def _is_negative(value: float) -> bool:
    return value < 0


def assert_positive(value: float) -> float:
    if _is_negative(value):
        raise ValueError("negative amount")
    return value
