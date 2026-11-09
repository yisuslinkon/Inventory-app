"""Conexión SQLite con transacciones explícitas."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from .migrator import migrate


def now_str() -> str:
    """Fecha/hora local como texto ISO (YYYY-MM-DD HH:MM:SS)."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Database:
    """Envoltorio de una conexión SQLite.

    La conexión corre en modo manual de transacciones (isolation_level=None),
    y `transaction()` abre BEGIN IMMEDIATE / COMMIT / ROLLBACK.
    """

    def __init__(self, path: Path | str):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.isolation_level = None
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.clock = now_str  # inyectable en tests
        migrate(self.conn)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        if self.conn.in_transaction:
            # Transacción anidada: se reutiliza la externa.
            yield self.conn
            return
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield self.conn
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise
        else:
            self.conn.execute("COMMIT")

    def close(self) -> None:
        self.conn.close()
