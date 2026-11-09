"""Diálogos amigables en español y decorador para capturar errores en los slots."""
from __future__ import annotations

import functools
import logging

from PySide6.QtWidgets import QMessageBox, QWidget

from ... import strings as S
from ...services.errors import AppError

log = logging.getLogger("inventario")


def show_error(parent: QWidget | None, error: BaseException | str) -> None:
    if isinstance(error, AppError):
        text, icon = str(error), QMessageBox.Icon.Warning
    elif isinstance(error, str):
        text, icon = error, QMessageBox.Icon.Warning
    else:
        text, icon = S.ERR_UNEXPECTED.format(detail=error), QMessageBox.Icon.Critical
    box = QMessageBox(parent)
    box.setIcon(icon)
    box.setWindowTitle(S.DLG_ERROR_TITLE)
    box.setText(text)
    box.addButton(S.BTN_OK, QMessageBox.ButtonRole.AcceptRole)
    box.exec()


def show_info(parent: QWidget | None, text: str, title: str | None = None) -> None:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(title or S.DLG_INFO_TITLE)
    box.setText(text)
    box.addButton(S.BTN_OK, QMessageBox.ButtonRole.AcceptRole)
    box.exec()


def confirm(parent: QWidget | None, text: str, ok_text: str, title: str | None = None) -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(title or S.DLG_CONFIRM_TITLE)
    box.setText(text)
    yes = box.addButton(ok_text, QMessageBox.ButtonRole.AcceptRole)
    box.addButton(S.BTN_CANCEL, QMessageBox.ButtonRole.RejectRole)
    box.exec()
    return box.clickedButton() is yes


def guarded(method):
    """Envuelve un slot `def slot(self)`: los errores se muestran en un diálogo."""

    @functools.wraps(method)
    def wrapper(self, *_signal_args):
        try:
            return method(self)
        except AppError as e:
            show_error(self, e)
        except Exception as e:  # noqa: BLE001 - nunca dejar que la app se cierre
            log.exception("Error inesperado en %s", method.__name__)
            show_error(self, e)

    return wrapper
