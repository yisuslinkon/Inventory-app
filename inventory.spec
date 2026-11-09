# -*- mode: python ; coding: utf-8 -*-
# Spec de PyInstaller compartido por macOS (.app) y Windows (carpeta con .exe).
# Uso:  pyinstaller --noconfirm --clean inventory.spec
import re
import sys
from pathlib import Path

root = Path(SPECPATH)
version = re.search(r'APP_VERSION\s*=\s*"([^"]+)"',
                    (root / "src" / "inventory_app" / "config.py").read_text()).group(1)

a = Analysis(
    [str(root / "run.py")],
    pathex=[str(root / "src")],
    datas=[(str(root / "src" / "inventory_app" / "db" / "migrations"),
            "inventory_app/db/migrations")],
    hiddenimports=[],
    excludes=["tkinter", "matplotlib", "numpy", "PySide6.QtWebEngineCore",
              "PySide6.QtWebEngineWidgets", "PySide6.QtQml", "PySide6.QtQuick"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Inventario",
    console=False,            # equivale a --windowed
    argv_emulation=False,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="Inventario")

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Inventario.app",
        icon=None,
        bundle_identifier="com.yisuslinkon.inventario",
        info_plist={
            "CFBundleName": "Inventario",
            "CFBundleDisplayName": "Inventario",
            "CFBundleShortVersionString": version,
            "CFBundleVersion": version,
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "11.0",
        },
    )
