from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit

from ...services.money import CurrencyFormat, format_money


class MoneyEdit(QLineEdit):
    """Campo de dinero: el usuario escribe '50.000' o '50000'; `value()` da un entero."""

    def __init__(self, fmt: CurrencyFormat, field: str, parent=None):
        super().__init__(parent)
        self.fmt = fmt
        self.field = field
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setPlaceholderText(format_money(0, "", fmt.decimals).strip())
        self.editingFinished.connect(self._reformat)

    def value(self) -> int:
        return self.fmt.parse(self.text(), self.field)

    def set_value(self, amount: int) -> None:
        self.setText(format_money(amount, "", self.fmt.decimals).strip())

    def _reformat(self) -> None:
        try:
            self.set_value(self.value())
        except Exception:  # noqa: BLE001 - el error se informa al guardar
            pass
