"""Dinero como enteros en la unidad mínima. Sin floats en ningún punto."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .. import strings as S
from .errors import ValidationError


@dataclass(frozen=True)
class CurrencyFormat:
    code: str = "COP"
    symbol: str = "$"
    decimals: int = 0

    def format(self, amount: int) -> str:
        return format_money(amount, self.symbol, self.decimals)

    def parse(self, text: str, field: str = "Monto") -> int:
        return parse_money(text, self.decimals, field)

    def plain(self, amount: int) -> str:
        return to_plain(amount, self.decimals)


def _group(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def format_money(amount: int, symbol: str = "$", decimals: int = 0) -> str:
    """1234567 -> '$ 1.234.567' (decimales con coma si decimals > 0)."""
    sign = "-" if amount < 0 else ""
    amount = abs(int(amount))
    if decimals <= 0:
        return f"{sign}{symbol} {_group(amount)}"
    factor = 10 ** decimals
    whole, frac = divmod(amount, factor)
    return f"{sign}{symbol} {_group(whole)},{frac:0{decimals}d}"


def to_plain(amount: int, decimals: int = 0) -> str:
    """Para CSV: sin símbolo ni separadores de miles, punto decimal."""
    sign = "-" if amount < 0 else ""
    amount = abs(int(amount))
    if decimals <= 0:
        return f"{sign}{amount}"
    whole, frac = divmod(amount, 10 ** decimals)
    return f"{sign}{whole}.{frac:0{decimals}d}"


_CLEAN = re.compile(r"[^\d,.\-]")


def parse_money(text: str, decimals: int = 0, field: str = "Monto") -> int:
    """Convierte texto del usuario a entero en unidad mínima.

    Acepta '1.234.567', '1234567', '$ 1.234.567' y, con decimales, '1.234,56'.
    """
    err = ValidationError(S.ERR_INVALID_MONEY.format(field=field))
    if not isinstance(text, str):
        raise err
    cleaned = _CLEAN.sub("", text.strip())
    if not cleaned or cleaned in {"-", ",", "."} or cleaned.startswith("-"):
        raise err
    if decimals <= 0:
        # Solo se aceptan separadores de miles (punto o coma) entre grupos de 3.
        if re.fullmatch(r"\d+", cleaned):
            return int(cleaned)
        if re.fullmatch(r"\d{1,3}([.,]\d{3})+", cleaned):
            return int(re.sub(r"[.,]", "", cleaned))
        raise err
    # Con decimales: la coma es el separador decimal; el punto, el de miles.
    if cleaned.count(",") > 1:
        raise err
    whole_part, _, frac_part = cleaned.partition(",")
    whole_part = whole_part.replace(".", "")
    if not whole_part.isdigit() or (frac_part and not frac_part.isdigit()):
        raise err
    if len(frac_part) > decimals:
        raise err
    frac_part = frac_part.ljust(decimals, "0")
    return int(whole_part) * 10 ** decimals + int(frac_part or 0)
