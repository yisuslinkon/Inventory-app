from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QSpinBox)

from ... import strings as S
from ...context import AppContext
from ..util import display_dt
from ..widgets.dialogs import guarded, show_info
from ..widgets.product_picker import ProductPicker
from ..widgets.tables import (BAD, GOOD, RIGHT, SortItem, fill_table, make_table, tint)
from .base import BasePage, make_card

MAX_QTY = 10_000_000


class InventoryPage(BasePage):
    def __init__(self, ctx: AppContext):
        super().__init__(ctx, S.NAV_INVENTORY)
        card, lay = make_card()
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        self.picker = ProductPicker()
        self.current_stock = QLabel("")
        self.kind = QComboBox()
        for label, key in ((S.ADJ_RESTOCK, "restock"), (S.ADJ_LOSS, "loss"),
                           (S.ADJ_CORRECTION, "correction")):
            self.kind.addItem(label, key)
        self.qty_label = QLabel(S.LBL_QUANTITY)
        self.qty = QSpinBox()
        self.qty.setRange(0, MAX_QTY)
        self.note = QLineEdit()
        self.note.setPlaceholderText(S.LBL_NOTE_OPTIONAL)
        self.apply = QPushButton(S.BTN_APPLY_ADJUSTMENT)
        self.apply.setObjectName("Primary")

        grid.addWidget(QLabel(S.LBL_PRODUCT), 0, 0)
        grid.addWidget(self.picker, 0, 1, 1, 3)
        grid.addWidget(self.current_stock, 0, 4)
        grid.addWidget(QLabel(S.LBL_ADJ_TYPE), 1, 0)
        grid.addWidget(self.kind, 1, 1)
        grid.addWidget(self.qty_label, 1, 2)
        grid.addWidget(self.qty, 1, 3)
        grid.addWidget(QLabel(S.LBL_NOTE), 2, 0)
        grid.addWidget(self.note, 2, 1, 1, 3)
        grid.addWidget(self.apply, 2, 4)
        grid.setColumnStretch(1, 1)
        lay.addLayout(grid)
        self.body.addWidget(card)

        row = QHBoxLayout()
        self.show_all = QCheckBox(S.CHK_HISTORY_ALL)
        row.addWidget(QLabel(S.LBL_HISTORY))
        row.addStretch(1)
        row.addWidget(self.show_all)
        self.body.addLayout(row)

        self.table = make_table([S.COL_DATE, S.COL_PRODUCT, S.COL_TYPE, S.COL_CHANGE,
                                 S.COL_STOCK_AFTER, S.COL_NOTE], stretch=5)
        self.body.addWidget(self.table, 1)

        self.picker.currentIndexChanged.connect(lambda *_: self._on_product_changed())
        self.kind.currentIndexChanged.connect(lambda *_: self._on_kind_changed())
        self.show_all.toggled.connect(lambda *_: self._load_history())
        self.apply.clicked.connect(self.on_apply)

    # ------------------------------------------------------------------
    def refresh(self) -> None:
        self.picker.load(self.ctx.products.list())
        self._on_product_changed()

    def _on_product_changed(self) -> None:
        pid = self.picker.selected_id()
        if pid is None:
            self.current_stock.setText("")
        else:
            p = self.ctx.products.get(pid)
            self.current_stock.setText(f"{S.LBL_STOCK_CURRENT}: {p.stock}")
            if self.kind.currentData() == "correction":
                self.qty.setValue(p.stock)
        self._load_history()

    def _on_kind_changed(self) -> None:
        if self.kind.currentData() == "correction":
            self.qty_label.setText(S.LBL_REAL_COUNT)
            pid = self.picker.selected_id()
            if pid is not None:
                self.qty.setValue(self.ctx.products.get(pid).stock)
        else:
            self.qty_label.setText(S.LBL_QUANTITY)
            self.qty.setValue(0)

    def _load_history(self) -> None:
        pid = None if self.show_all.isChecked() else self.picker.selected_id()
        if pid is None and not self.show_all.isChecked():
            fill_table(self.table, [])
            return
        moves = self.ctx.inventory.history(pid)
        rows = []
        for m in moves:
            change = SortItem(f"{m.quantity:+d}", m.quantity, RIGHT)
            tint(change, GOOD if m.quantity > 0 else BAD)
            rows.append([
                SortItem(display_dt(m.created_at), m.created_at),
                SortItem(f"{m.product_name} ({m.sku})"),
                SortItem(S.MOVEMENT_LABELS.get(m.type, m.type)),
                change,
                SortItem(str(m.stock_after), m.stock_after, RIGHT),
                SortItem(m.note),
            ])
        fill_table(self.table, rows)
        self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)

    @guarded
    def on_apply(self) -> None:
        pid = self.picker.require_id()
        kind = self.kind.currentData()
        new_stock = self.ctx.inventory.adjust(pid, kind, self.qty.value(), self.note.text())
        self.note.clear()
        self.refresh()
        show_info(self, S.MSG_ADJUSTMENT_OK.format(stock=new_stock))
