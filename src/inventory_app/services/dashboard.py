from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..db.connection import Database
from .products import Product, ProductService


@dataclass(frozen=True)
class MonthSummary:
    revenue: int
    units: int
    profit: int


@dataclass(frozen=True)
class MonthPoint:
    year: int
    month: int
    revenue: int

    @property
    def label(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"


@dataclass(frozen=True)
class TopProduct:
    name: str
    sku: str
    units: int
    revenue: int


def month_bounds(year: int, month: int) -> tuple[str, str]:
    """[inicio, fin) del mes como texto comparable con created_at."""
    ny, nm = (year + 1, 1) if month == 12 else (year, month + 1)
    return f"{year:04d}-{month:02d}-01 00:00:00", f"{ny:04d}-{nm:02d}-01 00:00:00"


def _shift(year: int, month: int, delta: int) -> tuple[int, int]:
    idx = year * 12 + (month - 1) + delta
    return idx // 12, idx % 12 + 1


class DashboardService:
    def __init__(self, db: Database):
        self.db = db

    def month_summary(self, year: int, month: int) -> MonthSummary:
        start, end = month_bounds(year, month)
        r = self.db.conn.execute(
            "SELECT COALESCE(SUM(si.quantity * si.unit_price), 0) AS revenue,"
            " COALESCE(SUM(si.quantity), 0) AS units,"
            " COALESCE(SUM(si.quantity * (si.unit_price - si.unit_cost)), 0) AS profit"
            " FROM sale_items si JOIN sales s ON s.id = si.sale_id"
            " WHERE s.status = 'completed' AND s.created_at >= ? AND s.created_at < ?",
            (start, end),
        ).fetchone()
        return MonthSummary(r["revenue"], r["units"], r["profit"])

    def monthly_sales(self, year: int, month: int, months: int = 12) -> list[MonthPoint]:
        """Ingresos por mes de los últimos `months` meses terminando en (year, month)."""
        first_y, first_m = _shift(year, month, -(months - 1))
        start, _ = month_bounds(first_y, first_m)
        _, end = month_bounds(year, month)
        rows = self.db.conn.execute(
            "SELECT substr(s.created_at, 1, 7) AS ym,"
            " SUM(si.quantity * si.unit_price) AS revenue"
            " FROM sale_items si JOIN sales s ON s.id = si.sale_id"
            " WHERE s.status = 'completed' AND s.created_at >= ? AND s.created_at < ?"
            " GROUP BY ym",
            (start, end),
        )
        by_month = {r["ym"]: r["revenue"] for r in rows}
        points = []
        for i in range(months):
            y, m = _shift(first_y, first_m, i)
            points.append(MonthPoint(y, m, by_month.get(f"{y:04d}-{m:02d}", 0)))
        return points

    def top_products(self, year: int, month: int, limit: int = 5) -> list[TopProduct]:
        start, end = month_bounds(year, month)
        rows = self.db.conn.execute(
            "SELECT p.name, p.sku, SUM(si.quantity) AS units,"
            " SUM(si.quantity * si.unit_price) AS revenue"
            " FROM sale_items si JOIN sales s ON s.id = si.sale_id"
            " JOIN products p ON p.id = si.product_id"
            " WHERE s.status = 'completed' AND s.created_at >= ? AND s.created_at < ?"
            " GROUP BY p.id ORDER BY units DESC, revenue DESC, p.name LIMIT ?",
            (start, end, limit),
        )
        return [TopProduct(r["name"], r["sku"], r["units"], r["revenue"]) for r in rows]

    def low_stock(self) -> list[Product]:
        return ProductService(self.db).list(low_stock_only=True)

    @staticmethod
    def today() -> date:
        return date.today()
