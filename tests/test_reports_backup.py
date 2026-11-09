import csv
import sqlite3

import pytest

from inventory_app.db.connection import Database
from inventory_app.services.backup import export_backup, import_backup, validate_backup
from inventory_app.services.errors import BackupError, ValidationError
from inventory_app.services.money import CurrencyFormat
from inventory_app.services.reports import ReportService


def test_report_range_and_csv(db, sales, two_products, tmp_path):
    cam, gor = two_products
    db.clock = lambda: "2026-11-02 09:00:00"
    sales.create_sale([(cam, 2), (gor, 1)], note="mostrador")
    db.clock = lambda: "2026-11-20 09:00:00"
    s2 = sales.create_sale([(cam, 1)])
    sales.void_sale(s2)
    rep = ReportService(db)
    in_range = rep.sales_between("2026-11-01", "2026-11-10")
    assert len(in_range) == 1
    assert len(rep.sales_between("2026-11-01", "2026-11-30")) == 2
    assert len(rep.sales_between("2026-11-01", "2026-11-30", include_voided=False)) == 1

    out = tmp_path / "ventas.csv"
    n = rep.export_csv(out, in_range, CurrencyFormat())
    assert n == 2
    with open(out, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))
    assert rows[0][0] == "Venta" and len(rows) == 3
    assert rows[1][3:9] == ["CAM-001", "Camiseta", "2", "50000", "100000", "60000"]


def test_report_invalid_dates(db):
    rep = ReportService(db)
    with pytest.raises(ValidationError):
        rep.sales_between("2026-12-01", "2026-11-01")
    with pytest.raises(ValidationError):
        rep.sales_between("no-fecha", "2026-11-01")


def test_backup_roundtrip(tmp_path, db, two_products, sales):
    sales.create_sale([(two_products[0], 2)])
    backup = tmp_path / "copia.db"
    export_backup(db, backup)
    assert validate_backup(backup) >= 1

    other_path = tmp_path / "otra.db"
    other = Database(other_path)
    other.close()
    safety = import_backup(backup, other_path)
    assert safety is not None and safety.exists()
    restored = Database(other_path)
    assert restored.conn.execute("SELECT stock FROM products WHERE sku='CAM-001'").fetchone()[0] == 8
    assert restored.conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 1
    restored.close()


def test_import_rejects_garbage(tmp_path):
    bad = tmp_path / "malo.db"
    bad.write_text("esto no es sqlite")
    with pytest.raises(BackupError):
        validate_backup(bad)
    empty_db = tmp_path / "vacia.db"
    sqlite3.connect(empty_db).close()
    with pytest.raises(BackupError):
        validate_backup(empty_db)
    with pytest.raises(BackupError):
        validate_backup(tmp_path / "no-existe.db")


def test_import_rejects_newer_version(tmp_path, db):
    newer = tmp_path / "nueva.db"
    export_backup(db, newer)
    c = sqlite3.connect(newer)
    c.execute("PRAGMA user_version = 99")
    c.commit()
    c.close()
    with pytest.raises(BackupError):
        validate_backup(newer)
