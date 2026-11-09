"""Exportar/importar la base de datos. Funciones sin dependencias de Qt."""
from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from .. import strings as S
from ..db.connection import Database
from ..db.migrator import latest_version
from .errors import BackupError

REQUIRED_TABLES = {"products", "sales", "sale_items", "stock_movements", "settings"}


def export_backup(db: Database, dest: Path | str) -> None:
    """Copia consistente de la BD (API de backup de SQLite, segura con la app abierta)."""
    dest = Path(dest)
    if dest.exists():
        dest.unlink()
    target = sqlite3.connect(str(dest))
    try:
        db.conn.backup(target)
    finally:
        target.close()


def validate_backup(src: Path | str) -> int:
    """Verifica que `src` sea una BD de Inventario válida. Devuelve su user_version."""
    src = Path(src)
    if not src.is_file():
        raise BackupError(S.ERR_BACKUP_INVALID)
    try:
        conn = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
        try:
            if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise BackupError(S.ERR_BACKUP_INVALID)
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'")}
            if not REQUIRED_TABLES <= tables:
                raise BackupError(S.ERR_BACKUP_INVALID)
            version = conn.execute("PRAGMA user_version").fetchone()[0]
        finally:
            conn.close()
    except sqlite3.DatabaseError:
        raise BackupError(S.ERR_BACKUP_INVALID) from None
    if version > latest_version():
        raise BackupError(S.ERR_BACKUP_NEWER)
    return version


def import_backup(src: Path | str, db_path: Path | str) -> Path | None:
    """Reemplaza la BD en `db_path` por la copia `src`.

    El llamador debe cerrar su conexión antes y reabrir `Database(db_path)` después
    (eso aplica las migraciones pendientes). Antes de reemplazar se guarda una copia
    de seguridad automática; devuelve su ruta (o None si no había BD previa).
    """
    src, db_path = Path(src), Path(db_path)
    validate_backup(src)
    safety = None
    if db_path.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safety = db_path.with_name(f"{db_path.stem}-antes-de-importar-{stamp}{db_path.suffix}")
        shutil.copy2(db_path, safety)
    tmp = db_path.with_name(db_path.name + ".importando")
    shutil.copy2(src, tmp)
    tmp.replace(db_path)
    for ext in ("-wal", "-shm", "-journal"):
        db_path.with_name(db_path.name + ext).unlink(missing_ok=True)
    return safety
