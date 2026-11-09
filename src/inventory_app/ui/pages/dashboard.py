from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout

from ... import strings as S
from ...context import AppContext
from ..widgets.charts import MonthlyBarChart
from ..widgets.tables import RIGHT, SortItem, fill_table, make_table, paint_row
from .base import BasePage, make_card


class DashboardPage(BasePage):
    def __init__(self, ctx: AppContext):
        super().__init__(ctx, S.NAV_DASHBOARD)
        self.subtitle = QLabel("")
        self.subtitle.setObjectName("Muted")
        self.body.addWidget(self.subtitle)

        cards = QHBoxLayout()
        cards.setSpacing(14)
        self.kpi_revenue = self._kpi(cards, S.KPI_REVENUE)
        self.kpi_units = self._kpi(cards, S.KPI_UNITS)
        self.kpi_profit = self._kpi(cards, S.KPI_PROFIT)
        self.body.addLayout(cards)

        chart_card, cl = make_card()
        cl.addWidget(self._section(S.CHART_TITLE))
        self.chart = MonthlyBarChart()
        cl.addWidget(self.chart, 1)
        self.body.addWidget(chart_card, 3)

        bottom = QHBoxLayout()
        bottom.setSpacing(14)
        top_card, tl = make_card()
        tl.addWidget(self._section(S.TOP_TITLE))
        self.top_table = make_table([S.COL_PRODUCT, S.COL_UNITS, S.COL_REVENUE], stretch=0)
        self.top_empty = QLabel(S.TOP_EMPTY)
        self.top_empty.setObjectName("Muted")
        tl.addWidget(self.top_table, 1)
        tl.addWidget(self.top_empty)
        low_card, ll = make_card()
        ll.addWidget(self._section(S.LOW_TITLE))
        self.low_table = make_table([S.COL_PRODUCT, S.COL_STOCK, S.COL_MIN_STOCK], stretch=0)
        self.low_empty = QLabel(S.LOW_EMPTY)
        self.low_empty.setObjectName("Muted")
        ll.addWidget(self.low_table, 1)
        ll.addWidget(self.low_empty)
        bottom.addWidget(top_card, 1)
        bottom.addWidget(low_card, 1)
        self.body.addLayout(bottom, 3)

    def _section(self, text: str) -> QLabel:
        lbl = QLabel(text)
        f = lbl.font()
        f.setBold(True)
        lbl.setFont(f)
        return lbl

    def _kpi(self, layout: QHBoxLayout, title: str) -> QLabel:
        card, lay = make_card()
        t = QLabel(title)
        t.setObjectName("CardTitle")
        v = QLabel("—")
        f = v.font()
        f.setPointSizeF(f.pointSizeF() * 1.9)
        f.setBold(True)
        v.setFont(f)
        lay.addWidget(t)
        lay.addWidget(v)
        layout.addWidget(card, 1)
        return v

    def refresh(self) -> None:
        fmt = self.ctx.currency
        today = date.today()
        y, m = today.year, today.month
        self.subtitle.setText(S.DASH_SUBTITLE.format(month=S.MONTHS[m - 1], year=y))

        s = self.ctx.dashboard.month_summary(y, m)
        self.kpi_revenue.setText(fmt.format(s.revenue))
        self.kpi_units.setText(str(s.units))
        self.kpi_profit.setText(fmt.format(s.profit))

        self.chart.set_data(self.ctx.dashboard.monthly_sales(y, m, 12), fmt)

        top = self.ctx.dashboard.top_products(y, m, 5)
        fill_table(self.top_table, [[
            SortItem(t.name), SortItem(str(t.units), t.units, RIGHT),
            SortItem(fmt.format(t.revenue), t.revenue, RIGHT)] for t in top])
        self.top_table.setVisible(bool(top))
        self.top_empty.setVisible(not top)

        low = self.ctx.dashboard.low_stock()
        rows = []
        for p in low:
            cells = [SortItem(p.name), SortItem(str(p.stock), p.stock, RIGHT),
                     SortItem(str(p.min_stock), p.min_stock, RIGHT)]
            paint_row(cells)
            rows.append(cells)
        fill_table(self.low_table, rows)
        self.low_table.setVisible(bool(low))
        self.low_empty.setVisible(not low)
