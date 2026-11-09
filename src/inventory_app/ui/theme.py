"""Aspecto visual único para Mac y Windows (estilo Fusion + paleta clara fija)."""
from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

PRIMARY = "#2f6fed"
ALERT_BG = "#fdecea"
ALERT_FG = "#8a1c13"
MUTED = "#6b7385"
GOOD = "#1b7f3b"
BAD = "#b3261e"

STYLESHEET = f"""
QWidget#Page {{ background: #f4f5f7; }}
QListWidget#Sidebar {{ background: #1f2a44; color: #dfe5f2; border: none; outline: 0;
    padding-top: 12px; }}
QListWidget#Sidebar::item {{ padding: 12px 18px; }}
QListWidget#Sidebar::item:selected {{ background: {PRIMARY}; color: white; }}
QFrame#Card {{ background: white; border: 1px solid #e1e4ea; border-radius: 8px; }}
QLabel#CardTitle {{ color: {MUTED}; }}
QLabel#Muted {{ color: {MUTED}; }}
QPushButton {{ padding: 6px 14px; border: 1px solid #c8ccd6; border-radius: 6px;
    background: white; }}
QPushButton:hover {{ background: #eef1f7; }}
QPushButton:disabled {{ color: #9aa0ad; background: #f4f5f7; }}
QPushButton#Primary {{ background: {PRIMARY}; color: white; border: 1px solid #2a63d4; }}
QPushButton#Primary:hover {{ background: #2a63d4; }}
QPushButton#Primary:disabled {{ background: #a9bfee; border-color: #a9bfee; color: white; }}
QPushButton#Danger {{ color: {BAD}; }}
QLineEdit {{ padding: 5px 8px; border: 1px solid #c8ccd6; border-radius: 6px;
    background: white; }}
QTableWidget {{ background: white; alternate-background-color: #f8f9fb;
    border: 1px solid #e1e4ea; selection-background-color: #cfe0ff;
    selection-color: #111111; }}
QHeaderView::section {{ background: #eef0f4; padding: 6px; border: none;
    border-bottom: 1px solid #d5d9e2; font-weight: bold; }}
QTabWidget::pane {{ border: 1px solid #e1e4ea; background: #f4f5f7; top: -1px; }}
"""


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor("#f4f5f7"))
    p.setColor(QPalette.ColorRole.WindowText, QColor("#1b2233"))
    p.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.AlternateBase, QColor("#f8f9fb"))
    p.setColor(QPalette.ColorRole.Text, QColor("#1b2233"))
    p.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.ButtonText, QColor("#1b2233"))
    p.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.ToolTipText, QColor("#1b2233"))
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#8a91a0"))
    p.setColor(QPalette.ColorRole.Highlight, QColor(PRIMARY))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(p)
    app.setStyleSheet(STYLESHEET)
