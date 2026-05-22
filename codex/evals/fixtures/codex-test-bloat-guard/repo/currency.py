def parse_currency(text: str) -> float:
    if not text:
        raise ValueError("empty input")
    cleaned = text.replace(",", "").lstrip("$")
    return float(cleaned)
