from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton)

from ... import strings as S
from ...context import AppContext
from ..widgets.dialogs import confirm, guarded, show_info
from .base import BasePage, make_card


class SettingsPage(BasePage):
    data_replaced = Signal()   # tras importar una copia o cambiar la moneda

    def __init__(self, ctx: AppContext):
        super().__init__(ctx, S.NAV_SETTINGS)

        # ---- Respaldo
        card, lay = make_card()
        title = QLabel(S.BACKUP_TITLE)
        f = title.font()
        f.setBold(True)
        title.setFont(f)
        lay.addWidget(title)
        hint = QLabel(S.BACKUP_HINT)
        hint.setWordWrap(True)
        hint.setObjectName("Muted")
        lay.addWidget(hint)
        row = QHBoxLayout()
        self.btn_export = QPushButton(S.BTN_EXPORT_DB)
        self.btn_export.setObjectName("Primary")
        self.btn_import = QPushButton(S.BTN_IMPORT_DB)
        row.addWidget(self.btn_export)
        row.addWidget(self.btn_import)
        row.addStretch(1)
        lay.addLayout(row)
        self.path_label = QLabel("")
        self.path_label.setObjectName("Muted")
        self.path_label.setWordWrap(True)
        self.path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.path_label)
        self.body.addWidget(card)

        # ---- Moneda
        card2, lay2 = make_card()
        t2 = QLabel(S.CURRENCY_TITLE)
        t2.setFont(f)
        lay2.addWidget(t2)
        form = QFormLayout()
        self.code = QLineEdit()
        self.code.setMaxLength(6)
        self.symbol = QLineEdit()
        self.symbol.setMaxLength(6)
        self.decimals = QComboBox()
        for n in (0, 1, 2):
            self.decimals.addItem(str(n), n)
        form.addRow(S.LBL_CURRENCY_CODE, self.code)
        form.addRow(S.LBL_CURRENCY_SYMBOL, self.symbol)
        form.addRow(S.LBL_CURRENCY_DECIMALS, self.decimals)
        lay2.addLayout(form)
        self.decimals_hint = QLabel(S.CURRENCY_DECIMALS_LOCKED)
        self.decimals_hint.setObjectName("Muted")
        self.decimals_hint.setWordWrap(True)
        lay2.addWidget(self.decimals_hint)
        self.btn_save_currency = QPushButton(S.BTN_SAVE)
        self.btn_save_currency.setObjectName("Primary")
        lay2.addWidget(self.btn_save_currency)
        self.preview = QLabel("")
        lay2.addWidget(self.preview)
        self.body.addWidget(card2)
        self.body.addStretch(1)

        self.btn_export.clicked.connect(self.on_export)
        self.btn_import.clicked.connect(self.on_import)
        self.btn_save_currency.clicked.connect(self.on_save_currency)

    def refresh(self) -> None:
        self.path_label.setText(S.DATA_FILE_LOCATION.format(path=self.ctx.db_path))
        c = self.ctx.currency
        self.code.setText(c.code)
        self.symbol.setText(c.symbol)
        self.decimals.setCurrentIndex(max(0, self.decimals.findData(c.decimals)))
        locked = self.ctx.has_data()
        self.decimals.setEnabled(not locked)
        self.decimals_hint.setVisible(locked)
        self.preview.setText(S.CURRENCY_PREVIEW.format(example=c.format(1234567 if c.decimals == 0
                                                                       else 123456789)))

    @guarded
    def on_export(self) -> None:
        default = f"inventario-{date.today():%Y%m%d}.db"
        path, _ = QFileDialog.getSaveFileName(self, S.DLG_EXPORT_DB, default, S.FILTER_DB)
        if not path:
            return
        self.ctx.export_backup(path)
        show_info(self, S.MSG_BACKUP_OK.format(path=path))

    @guarded
    def on_import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, S.DLG_IMPORT_DB, "", S.FILTER_DB)
        if not path:
            return
        if not confirm(self, S.CONFIRM_IMPORT_DB, S.BTN_IMPORT_CONFIRM):
            return
        safety = self.ctx.import_backup(path)
        self.refresh()
        self.data_replaced.emit()
        extra = S.MSG_IMPORT_SAFETY.format(path=safety) if safety else ""
        show_info(self, S.MSG_IMPORT_OK + extra)

    @guarded
    def on_save_currency(self) -> None:
        self.ctx.settings.set_currency(self.code.text(), self.symbol.text(),
                                       self.decimals.currentData())
        self.refresh()
        self.data_replaced.emit()
        show_info(self, S.MSG_CURRENCY_SAVED)
