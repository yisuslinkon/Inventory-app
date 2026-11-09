from __future__ import annotations

from PySide6.QtCharts import (QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView,
                              QValueAxis)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QCursor, QPainter
from PySide6.QtWidgets import QToolTip

from ... import strings as S
from ...services.dashboard import MonthPoint
from ...services.money import CurrencyFormat
from ..theme import PRIMARY


class MonthlyBarChart(QChartView):
    """Barras de ingresos por mes (QtCharts)."""

    def __init__(self, parent=None):
        self._chart = QChart()
        super().__init__(self._chart, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMinimumHeight(240)
        self._chart.legend().hide()
        self._chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self._chart.setBackgroundRoundness(0)
        self._chart.setBackgroundBrush(QColor("white"))
        self._points: list[MonthPoint] = []
        self._fmt = CurrencyFormat()

    def set_data(self, points: list[MonthPoint], fmt: CurrencyFormat) -> None:
        self._points, self._fmt = points, fmt
        chart = self._chart
        chart.removeAllSeries()
        for axis in list(chart.axes()):
            chart.removeAxis(axis)

        divisor = 10 ** fmt.decimals  # solo para dibujar; los datos siguen siendo enteros
        bars = QBarSet(S.CHART_SERIES)
        bars.setColor(QColor(PRIMARY))
        bars.setBorderColor(QColor(PRIMARY))
        for p in points:
            bars.append(p.revenue / divisor)

        series = QBarSeries()
        series.append(bars)
        series.setBarWidth(0.7)
        series.hovered.connect(self._on_hover)
        chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append([f"{S.MONTHS_SHORT[p.month - 1]} {str(p.year)[2:]}" for p in points])
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        top = max((p.revenue for p in points), default=0) / divisor
        axis_y = QValueAxis()
        axis_y.setRange(0, top * 1.1 if top > 0 else 1)
        axis_y.setLabelFormat("%.0f")
        axis_y.applyNiceNumbers()
        axis_y.setGridLineColor(QColor("#e6e8ee"))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

    def _on_hover(self, state: bool, index: int, _barset) -> None:
        if state and 0 <= index < len(self._points):
            p = self._points[index]
            QToolTip.showText(
                QCursor.pos(),
                f"{S.MONTHS[p.month - 1]} {p.year}: {self._fmt.format(p.revenue)}", self)
        else:
            QToolTip.hideText()
