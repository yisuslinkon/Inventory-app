"""Contenedor de servicios. Sin dependencias de Qt (la UI lo recibe ya armado)."""
from __future__ import annotations

from pathlib import Path

from .db.connection import Database
from .services.backup import export_backup, import_backup
from .services.dashboard import DashboardService
from .services.inventory import InventoryService
from .services.money import CurrencyFormat
from .services.products import ProductService
from .services.reports import ReportService
from .services.sales import SaleService
from .services.settings import SettingsService


class AppContext:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self._open()

    def _open(self) -> None:
        self.db = Database(self.db_path)
        self.products = ProductService(self.db)
        self.inventory = InventoryService(self.db)
        self.sales = SaleService(self.db)
        self.dashboard = DashboardService(self.db)
        self.reports = ReportService(self.db)
        self.settings = SettingsService(self.db)

    @property
    def currency(self) -> CurrencyFormat:
        return self.settings.currency()

    def has_data(self) -> bool:
        c = self.db.conn
        return bool(c.execute(
            "SELECT (SELECT COUNT(*) FROM products) + (SELECT COUNT(*) FROM sales)").fetchone()[0])

    def export_backup(self, dest: Path | str) -> None:
        export_backup(self.db, dest)

    def import_backup(self, src: Path | str) -> Path | None:
        """Reemplaza la BD por la copia `src` y reabre las conexiones."""
        self.db.close()
        try:
            return import_backup(src, self.db_path)
        finally:
            self._open()
