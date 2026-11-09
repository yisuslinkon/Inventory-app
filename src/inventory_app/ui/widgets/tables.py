from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from ..theme import ALERT_BG, ALERT_FG, BAD, GOOD, MUTED

RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
LEFT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
CENTER = Qt.AlignmentFlag.AlignCenter


class SortItem(QTableWidgetItem):
    """Celda que ordena por una clave (número o texto) en vez del texto mostrado."""

    def __init__(self, text: str, key=None, align=LEFT):
        super().__init__(text)
        self._key = text.lower() if key is None else key
        self.setTextAlignment(align)

    def __lt__(self, other):
        if isinstance(other, SortItem):
            try:
                return self._key < other._key
            except TypeError:
                return str(self._key) < str(other._key)
        return super().__lt__(other)


def make_table(headers: list[str], stretch: int | None = 0) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.setAlternatingRowColors(True)
    t.setShowGrid(False)
    t.verticalHeader().setVisible(False)
    t.verticalHeader().setDefaultSectionSize(32)
    t.setSortingEnabled(True)
    h = t.horizontalHeader()
    h.setHighlightSections(False)
    for i in range(len(headers)):
        mode = (QHeaderView.ResizeMode.Stretch if i == stretch
                else QHeaderView.ResizeMode.ResizeToContents)
        h.setSectionResizeMode(i, mode)
    return t


def fill_table(table: QTableWidget, rows: list[list[QTableWidgetItem]], ids: list | None = None):
    """Rellena la tabla. `ids[i]` se guarda en la primera celda de la fila i."""
    table.setSortingEnabled(False)
    table.setRowCount(len(rows))
    for r, cells in enumerate(rows):
        for c, item in enumerate(cells):
            if c == 0 and ids is not None:
                item.setData(Qt.ItemDataRole.UserRole, ids[r])
            table.setItem(r, c, item)
    table.setSortingEnabled(True)


def selected_id(table: QTableWidget):
    row = table.currentRow()
    if row < 0:
        return None
    item = table.item(row, 0)
    return item.data(Qt.ItemDataRole.UserRole) if item else None


def paint_row(cells: list[QTableWidgetItem], bg: str = ALERT_BG, fg: str = ALERT_FG) -> None:
    for item in cells:
        item.setBackground(QColor(bg))
        item.setForeground(QColor(fg))


def tint(item: QTableWidgetItem, color: str) -> None:
    item.setForeground(QColor(color))


__all__ = ["SortItem", "make_table", "fill_table", "selected_id", "paint_row", "tint",
           "RIGHT", "LEFT", "CENTER", "GOOD", "BAD", "MUTED"]
