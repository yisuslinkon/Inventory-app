from __future__ import annotations


def display_dt(value: str | None) -> str:
    """'2026-11-08 14:30:00' -> '08/11/2026 14:30'."""
    if not value:
        return ""
    date_part, _, time_part = value.partition(" ")
    try:
        y, m, d = date_part.split("-")
    except ValueError:
        return value
    return f"{d}/{m}/{y} {time_part[:5]}".strip()
