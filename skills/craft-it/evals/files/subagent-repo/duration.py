"""Parse duration strings such as "90s" or "5m" into seconds."""

UNITS = {"s": 1, "m": 60}


def parse(text):
    number, unit = text[:-1], text[-1:]
    if unit not in UNITS or not number.isdigit():
        raise ValueError(f"bad duration: {text!r}")
    return int(number) * UNITS[unit]
