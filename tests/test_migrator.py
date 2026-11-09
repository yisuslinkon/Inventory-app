import sqlite3

from inventory_app.db.connection import Database
from inventory_app.db.migrator import latest_version, migrate


def test_fresh_db_is_migrated(tmp_path):
    d = Database(tmp_path / "x.db")
    assert d.conn.execute("PRAGMA user_version").fetchone()[0] == latest_version()
    tables = {r[0] for r in d.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"products", "sales", "sale_items", "stock_movements", "settings"} <= tables
    assert d.conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    d.close()


def test_migrate_is_idempotent_and_applies_new_files(tmp_path):
    mig = tmp_path / "migs"
    mig.mkdir()
    (mig / "001_a.sql").write_text("CREATE TABLE a (id INTEGER);")
    conn = sqlite3.connect(":memory:")
    conn.isolation_level = None
    assert migrate(conn, mig) == 1
    assert migrate(conn, mig) == 1
    (mig / "002_b.sql").write_text("CREATE TABLE b (id INTEGER);\nINSERT INTO b VALUES (1);")
    assert migrate(conn, mig) == 2
    assert conn.execute("SELECT COUNT(*) FROM b").fetchone()[0] == 1


def test_failed_migration_rolls_back(tmp_path):
    mig = tmp_path / "migs"
    mig.mkdir()
    (mig / "001_a.sql").write_text("CREATE TABLE a (id INTEGER);")
    (mig / "002_bad.sql").write_text("CREATE TABLE c (id INTEGER);\nTHIS IS NOT SQL;")
    conn = sqlite3.connect(":memory:")
    conn.isolation_level = None
    try:
        migrate(conn, mig)
    except sqlite3.Error:
        pass
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 1
    assert conn.execute("SELECT name FROM sqlite_master WHERE name='c'").fetchone() is None
