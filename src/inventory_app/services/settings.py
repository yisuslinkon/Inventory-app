from __future__ import annotations

from ..db.connection import Database
from .errors import ValidationError
from .money import CurrencyFormat


class SettingsService:
    def __init__(self, db: Database):
        self.db = db

    def get(self, key: str, default: str = "") -> str:
        row = self.db.conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set(self, key: str, value: str) -> None:
        with self.db.transaction() as c:
            c.execute(
                "INSERT INTO settings(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def currency(self) -> CurrencyFormat:
        try:
            decimals = int(self.get("currency_decimals", "0"))
        except ValueError:
            decimals = 0
        return CurrencyFormat(
            code=self.get("currency_code", "COP"),
            symbol=self.get("currency_symbol", "$"),
            decimals=max(0, min(decimals, 4)),
        )

    def set_currency(self, code: str, symbol: str, decimals: int) -> None:
        code, symbol = code.strip().upper(), symbol.strip()
        if not code or not symbol or not (0 <= decimals <= 4):
            raise ValidationError("Configuración de moneda no válida.")
        self.set("currency_code", code)
        self.set("currency_symbol", symbol)
        self.set("currency_decimals", str(decimals))
