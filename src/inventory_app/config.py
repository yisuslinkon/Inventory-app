"""Configuración global y rutas del sistema de archivos (multiplataforma)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Kikario"
APP_VERSION = "1.0.0"
DB_FILENAME = "kikario.db"
ENV_DATA_DIR = "KIKARIO_DATA_DIR"   # permite usar otra carpeta de datos (p. ej. en desarrollo)


def is_custom_data_dir() -> bool:
    """True si se está usando una carpeta de datos distinta a la del sistema (modo desarrollo)."""
    return bool(os.environ.get(ENV_DATA_DIR))


def data_dir() -> Path:
    """Carpeta de datos del usuario según el SO.

    macOS:   ~/Library/Application Support/Kikario
    Windows: %APPDATA%\\Kikario

    Si existe la variable de entorno KIKARIO_DATA_DIR se usa esa carpeta. `run.py` la
    define automáticamente (./datos-dev) al ejecutar desde el código fuente, así los datos
    de prueba nunca se mezclan con los de la app instalada.
    """
    override = os.environ.get(ENV_DATA_DIR)
    if override:
        path = Path(override).expanduser().resolve()
    else:
        from platformdirs import user_data_dir

        path = Path(user_data_dir(APP_NAME, appauthor=False, roaming=True))
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return data_dir() / DB_FILENAME


def resource_dir() -> Path:
    """Carpeta de recursos (funciona en desarrollo y dentro de PyInstaller)."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / "inventory_app"
    return Path(__file__).resolve().parent
