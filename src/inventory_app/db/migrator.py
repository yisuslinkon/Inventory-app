"""Migraciones SQL versionadas con PRAGMA user_version.

Los archivos son `NNN_nombre.sql` dentro de db/migrations. Cada migración
se aplica en su propia transacción, y user_version sube al número NNN.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
_NAME = re.compile(r"^(\d{3})_.+\.sql$")


def _migration_files(directory: Path | None = None) -> list[tuple[int, Path]]:
    directory = directory or _resolve_dir()
    found = []
    for p in directory.iterdir():
        m = _NAME.match(p.name)
        if m:
            found.append((int(m.group(1)), p))
    return sorted(found)


def _resolve_dir() -> Path:
    # En PyInstaller los .sql se empaquetan como datos (ver inventory.spec).
    import sys

    base = getattr(sys, "_MEIPASS", None)
    if base:
        packed = Path(base) / "inventory_app" / "db" / "migrations"
        if packed.exists():
            return packed
    return MIGRATIONS_DIR


def latest_version(directory: Path | None = None) -> int:
    files = _migration_files(directory)
    return files[-1][0] if files else 0


def current_version(conn: sqlite3.Connection) -> int:
    return conn.execute("PRAGMA user_version").fetchone()[0]


def migrate(conn: sqlite3.Connection, directory: Path | None = None) -> int:
    """Aplica las migraciones pendientes. Devuelve la versión final."""
    version = current_version(conn)
    for number, path in _migration_files(directory):
        if number <= version:
            continue
        script = path.read_text(encoding="utf-8")
        in_manual = conn.isolation_level is None
        try:
            if in_manual:
                conn.execute("BEGIN IMMEDIATE")
            for stmt in _split_statements(script):
                conn.execute(stmt)
            conn.execute(f"PRAGMA user_version = {number}")
            if in_manual:
                conn.execute("COMMIT")
        except BaseException:
            if in_manual and conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        version = number
    return version


def _split_statements(script: str) -> list[str]:
    """Divide un script en sentencias completas usando sqlite3.complete_statement."""
    statements, buf = [], ""
    for line in script.splitlines(keepends=True):
        buf += line
        if sqlite3.complete_statement(buf):
            if buf.strip():
                statements.append(buf.strip())
            buf = ""
    if buf.strip():
        statements.append(buf.strip())
    return statements
