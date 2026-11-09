"""Punto de entrada de la aplicación."""
from __future__ import annotations

import logging
import sys

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtWidgets import QApplication, QMessageBox

from . import config
from . import strings as S
from .context import AppContext
from .ui.main_window import MainWindow
from .ui.theme import apply_theme
from .ui.widgets.dialogs import show_error


def _setup_logging() -> None:
    try:
        logging.basicConfig(
            filename=config.data_dir() / "inventario.log", level=logging.WARNING,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s", encoding="utf-8")
    except OSError:
        logging.basicConfig(level=logging.WARNING)


def _setup_locale(app: QApplication) -> list[QTranslator]:
    """Español para calendario, diálogos de archivo y botones estándar de Qt."""
    QLocale.setDefault(QLocale(QLocale.Language.Spanish, QLocale.Country.Colombia))
    translators = []
    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    for name in ("qtbase", "qt"):
        tr = QTranslator()
        try:
            if tr.load(QLocale(), name, "_", path):
                app.installTranslator(tr)
                translators.append(tr)  # mantener referencia viva
        except Exception:  # noqa: BLE001 - las traducciones son opcionales
            pass
    return translators


def _selftest() -> int:
    """Prueba de humo para la app empaquetada: `Inventario --selftest`.

    Usa una base de datos temporal (no toca la del usuario), crea un producto y una
    venta, y dibuja todas las páginas. Escribe el resultado en un archivo de texto.
    """
    import tempfile
    from pathlib import Path

    out = Path(tempfile.gettempdir()) / "inventario-selftest.txt"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            ctx = AppContext(Path(tmp) / "selftest.db")
            pid = ctx.products.create("Producto de prueba", "TEST-1", "Prueba", 1000, 2500, 5, 1)
            ctx.sales.create_sale([(pid, 2)])
            window = MainWindow(ctx)
            for row in range(window.stack.count()):
                window.sidebar.setCurrentRow(row)
            window.show()
            QApplication.processEvents()
            ctx.db.close()
        out.write_text("OK\n", encoding="utf-8")
        print("selftest OK")
        return 0
    except Exception as e:  # noqa: BLE001
        import traceback

        out.write_text("FALLO\n" + traceback.format_exc(), encoding="utf-8")
        print("selftest FALLO:", e)
        return 1


def main() -> int:
    _setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    apply_theme(app)
    _translators = _setup_locale(app)
    if "--selftest" in sys.argv:
        return _selftest()

    def excepthook(exc_type, exc, tb):
        logging.getLogger("inventario").error("Excepción no controlada", exc_info=(exc_type, exc, tb))
        show_error(None, exc)

    sys.excepthook = excepthook

    try:
        ctx = AppContext(config.db_path())
    except Exception as e:  # noqa: BLE001
        logging.getLogger("inventario").exception("No se pudo abrir la base de datos")
        box = QMessageBox(QMessageBox.Icon.Critical, S.DLG_ERROR_TITLE,
                          S.ERR_DB_OPEN.format(path=config.db_path(), detail=e))
        box.addButton(S.BTN_OK, QMessageBox.ButtonRole.AcceptRole)
        box.exec()
        return 1

    window = MainWindow(ctx)
    window.show()
    return app.exec()
