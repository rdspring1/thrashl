def parse_currency(s: str) -> float:
    if not s:
        raise ValueError("empty currency string")
    return float(s.replace("$", "").replace(",", ""))


def round_cents(value: float) -> float:
    return round(value, 2)
