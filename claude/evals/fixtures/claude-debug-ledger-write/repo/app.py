def parse_amount(text: str) -> float:
    cleaned = text.replace(",", "")
    return float(cleaned[2:])


def compute_total(amounts: list[str]) -> float:
    total = 0.0
    for a in amounts:
        total += parse_amount(a)
    return total
