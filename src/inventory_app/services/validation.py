"""Validadores pequeños y reutilizables."""
from __future__ import annotations

from .. import strings as S
from .errors import ValidationError


def as_int(value, field: str, *, minimum: int | None = None, positive: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            value = int(value.strip())
        else:
            raise ValidationError(S.ERR_INVALID_INT.format(field=field))
    if positive and value <= 0:
        raise ValidationError(S.ERR_MUST_BE_POSITIVE.format(field=field))
    if minimum is not None and value < minimum:
        raise ValidationError(S.ERR_NEGATIVE.format(field=field))
    return value


def required_text(value, message: str) -> str:
    text = (value or "").strip() if isinstance(value, str) or value is None else str(value).strip()
    if not text:
        raise ValidationError(message)
    return text
