from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (QHBoxLayout, QListWidget, QListWidgetItem, QMainWindow,
                               QStackedWidget, QWidget)

from .. import strings as S
from ..config import APP_NAME, is_custom_data_dir
from ..context import AppContext
from .pages.dashboard import DashboardPage
from .pages.inventory import InventoryPage
from .pages.products import ProductsPage
from .pages.reports import ReportsPage
from .pages.sales import SalesPage
from .pages.settings import SettingsPage
from .widgets.dialogs import guarded


class MainWindow(QMainWindow):
    def __init__(self, ctx: AppContext):
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle(
            S.WINDOW_TITLE_DEV.format(app=APP_NAME) if is_custom_data_dir() else APP_NAME)
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)

        self.pages = [
            (S.NAV_DASHBOARD, DashboardPage(ctx)),
            (S.NAV_PRODUCTS, ProductsPage(ctx)),
            (S.NAV_INVENTORY, InventoryPage(ctx)),
            (S.NAV_SALES, SalesPage(ctx)),
            (S.NAV_REPORTS, ReportsPage(ctx)),
            (S.NAV_SETTINGS, SettingsPage(ctx)),
        ]

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(200)
        self.stack = QStackedWidget()
        for label, page in self.pages:
            item = QListWidgetItem(label)
            item.setSizeHint(QSize(200, 44))
            self.sidebar.addItem(item)
            self.stack.addWidget(page)

        root = QWidget()
        lay = QHBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.sidebar)
        lay.addWidget(self.stack, 1)
        self.setCentralWidget(root)

        self.sidebar.currentRowChanged.connect(self._on_nav)
        settings_page = self.pages[-1][1]
        settings_page.data_replaced.connect(self.refresh_current)
        self.sidebar.setCurrentRow(0)

    def _on_nav(self, row: int) -> None:
        if row < 0:
            return
        self.stack.setCurrentIndex(row)
        self.refresh_current()

    @guarded
    def refresh_current(self) -> None:
        self.pages[self.stack.currentIndex()][1].refresh()
