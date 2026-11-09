from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox

from ... import strings as S
from ...services.errors import ValidationError


class ProductPicker(QComboBox):
    """Lista desplegable con búsqueda por texto (nombre o SKU)."""

    def __init__(self, show_stock: bool = False, parent=None):
        super().__init__(parent)
        self.show_stock = show_stock
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setMinimumWidth(320)
        comp = self.completer()
        comp.setFilterMode(Qt.MatchFlag.MatchContains)
        comp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.lineEdit().setPlaceholderText(S.PICKER_PLACEHOLDER)

    def load(self, products) -> None:
        keep = self.selected_id()
        self.blockSignals(True)
        self.clear()
        for p in products:
            label = f"{p.name} — {p.sku}"
            if self.show_stock:
                label += f"  ({S.PICKER_STOCK}: {p.stock})"
            self.addItem(label, p.id)
        idx = self.findData(keep) if keep is not None else -1
        self.setCurrentIndex(idx)
        if idx < 0:
            self.setEditText("")
        self.blockSignals(False)

    def selected_id(self) -> int | None:
        text = self.currentText().strip()
        if not text:
            return None
        idx = self.findText(text, Qt.MatchFlag.MatchFixedString)
        return self.itemData(idx) if idx >= 0 else None

    def require_id(self) -> int:
        pid = self.selected_id()
        if pid is None:
            raise ValidationError(S.ERR_PICK_PRODUCT)
        return pid
