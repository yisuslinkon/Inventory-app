from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .. import strings as S
from ..db.connection import Database
from .errors import ValidationError
from .money import CurrencyFormat
from .sales import Sale, SaleService


def parse_iso_date(value: str | date, field: str = "Fecha") -> str:
    if isinstance(value, date):
        return value.isoformat()
    try:
        return date.fromisoformat(value.strip()).isoformat()
    except (ValueError, AttributeError):
        raise ValidationError(f"{field}: fecha no válida.") from None


class ReportService:
    def __init__(self, db: Database):
        self.db = db
        self.sales = SaleService(db)

    def sales_between(self, start, end, include_voided: bool = True) -> list[Sale]:
        s, e = parse_iso_date(start, "Desde"), parse_iso_date(end, "Hasta")
        if s > e:
            raise ValidationError(S.ERR_DATE_RANGE)
        return self.sales.list(s, e, include_voided, limit=1_000_000)

    def export_csv(self, path: Path | str, sales: list[Sale], fmt: CurrencyFormat) -> int:
        """Escribe un CSV con una fila por producto vendido. Devuelve nº de filas.

        UTF-8 con BOM y separador ';' para que Excel en español lo abra bien.
        """
        header = ["Venta", "Fecha", "Estado", "SKU", "Producto", "Cantidad",
                  "Precio unitario", "Total línea", "Utilidad línea", "Nota"]
        rows = 0
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(header)
            for sale in sales:
                for it in sale.items:
                    w.writerow([
                        sale.id, sale.created_at, S.SALE_STATUS_LABELS[sale.status],
                        it.sku, it.product_name, it.quantity, fmt.plain(it.unit_price),
                        fmt.plain(it.line_total), fmt.plain(it.line_profit), sale.note,
                    ])
                    rows += 1
        return rows
