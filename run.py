"""Lanzador: `python run.py` en desarrollo, y script de entrada de PyInstaller.

Al correr desde el código fuente, los datos van a ./datos-dev (no a la carpeta real de la
app instalada). La app compilada (PyInstaller) ignora esto y usa la carpeta del sistema.
Para elegir otra carpeta:  KIKARIO_DATA_DIR=/ruta python run.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(ROOT / "src"))
    os.environ.setdefault("KIKARIO_DATA_DIR", str(ROOT / "datos-dev"))

from inventory_app.main import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
