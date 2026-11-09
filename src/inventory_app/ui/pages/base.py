from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from ...context import AppContext


class BasePage(QWidget):
    """Página con título; las subclases añaden contenido a `self.body`."""

    def __init__(self, ctx: AppContext, title: str):
        super().__init__()
        self.ctx = ctx
        self.setObjectName("Page")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(24, 20, 24, 20)
        self.body.setSpacing(14)
        heading = QLabel(title)
        f = heading.font()
        f.setPointSizeF(f.pointSizeF() * 1.6)
        f.setBold(True)
        heading.setFont(f)
        self.body.addWidget(heading)

    def refresh(self) -> None:  # las subclases lo sobrescriben
        pass


def make_card() -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setObjectName("Card")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(8)
    return card, lay
