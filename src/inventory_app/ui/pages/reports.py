from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QCheckBox, QDateEdit, QFileDialog, QHBoxLayout, QLabel,
                               QPushButton)

from ... import strings as S
from ...context import AppContext
from ..util import display_dt
from ..widgets.dialogs import guarded, show_info
from ..widgets.tables import MUTED, RIGHT, SortItem, fill_table, make_table, tint
from .base import BasePage, make_card


def _iso(d: QDate) -> str:
    return f"{d.year():04d}-{d.month():02d}-{d.day():02d}"


class ReportsPage(BasePage):
    def __init__(self, ctx: AppContext):
        super().__init__(ctx, S.NAV_REPORTS)
        self._sales = []

        card, lay = make_card()
        row = QHBoxLayout()
        today = QDate.currentDate()
        self.start = self._date_edit(QDate(today.year(), today.month(), 1))
        self.end = self._date_edit(today)
        self.include_voided = QCheckBox(S.CHK_INCLUDE_VOIDED)
        self.btn_query = QPushButton(S.BTN_QUERY)
        self.btn_query.setObjectName("Primary")
        self.btn_export = QPushButton(S.BTN_EXPORT_CSV)
        row.addWidget(QLabel(S.LBL_FROM))
        row.addWidget(self.start)
        row.addWidget(QLabel(S.LBL_TO))
        row.addWidget(self.end)
        row.addWidget(self.include_voided)
        row.addStretch(1)
        row.addWidget(self.btn_query)
        row.addWidget(self.btn_export)
        lay.addLayout(row)
        self.summary = QLabel("")
        lay.addWidget(self.summary)
        self.body.addWidget(card)

        self.table = make_table([S.COL_SALE_NO, S.COL_DATE, S.COL_DETAIL, S.COL_UNITS,
                                 S.COL_TOTAL, S.COL_PROFIT, S.COL_STATUS], stretch=2)
        self.body.addWidget(self.table, 1)

        self.btn_query.clicked.connect(self.on_query)
        self.btn_export.clicked.connect(self.on_export)

    @staticmethod
    def _date_edit(d: QDate) -> QDateEdit:
        e = QDateEdit(d)
        e.setCalendarPopup(True)
        e.setDisplayFormat("dd/MM/yyyy")
        return e

    def refresh(self) -> None:
        self.on_query()

    @guarded
    def on_query(self) -> None:
        fmt = self.ctx.currency
        self._sales = self.ctx.reports.sales_between(
            _iso(self.start.date()), _iso(self.end.date()), self.include_voided.isChecked())
        rows = []
        for s in self._sales:
            cells = [
                SortItem(f"#{s.id}", s.id, RIGHT),
                SortItem(display_dt(s.created_at), s.created_at),
                SortItem(", ".join(f"{i.quantity}× {i.product_name}" for i in s.items)),
                SortItem(str(s.units), s.units, RIGHT),
                SortItem(fmt.format(s.total), s.total, RIGHT),
                SortItem(fmt.format(s.profit), s.profit, RIGHT),
                SortItem(S.SALE_STATUS_LABELS[s.status]),
            ]
            if s.status == "voided":
                for c in cells:
                    tint(c, MUTED)
            rows.append(cells)
        fill_table(self.table, rows, [s.id for s in self._sales])

        ok = [s for s in self._sales if s.status == "completed"]
        self.summary.setText(S.REPORT_SUMMARY.format(
            n=len(ok), units=sum(s.units for s in ok),
            total=fmt.format(sum(s.total for s in ok)),
            profit=fmt.format(sum(s.profit for s in ok))))

    @guarded
    def on_export(self) -> None:
        self.on_query()
        if not self._sales:
            show_info(self, S.MSG_NO_SALES_TO_EXPORT)
            return
        default = f"ventas_{_iso(self.start.date())}_{_iso(self.end.date())}.csv"
        path, _ = QFileDialog.getSaveFileName(self, S.DLG_EXPORT_CSV, default, S.FILTER_CSV)
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        n = self.ctx.reports.export_csv(path, self._sales, self.ctx.currency)
        show_info(self, S.MSG_CSV_OK.format(n=n, path=path))
