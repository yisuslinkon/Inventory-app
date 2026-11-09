from __future__ import annotations

from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QSpinBox, QVBoxLayout)

from ... import strings as S
from ...context import AppContext
from ...services.errors import AppError
from ..widgets.dialogs import confirm, guarded, show_error, show_info
from ..widgets.money_edit import MoneyEdit
from ..widgets.tables import (RIGHT, SortItem, fill_table, make_table, paint_row,
                              selected_id)
from .base import BasePage

MAX_QTY = 10_000_000


class ProductDialog(QDialog):
    def __init__(self, ctx: AppContext, product=None, parent=None):
        super().__init__(parent)
        self.ctx, self.product = ctx, product
        self.setWindowTitle(S.PRODUCT_EDIT_TITLE if product else S.PRODUCT_NEW_TITLE)
        self.setMinimumWidth(440)
        fmt = ctx.currency

        self.name = QLineEdit()
        self.sku = QLineEdit()
        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems(ctx.products.categories())
        self.category.setCurrentText("")
        self.cost = MoneyEdit(fmt, S.FIELD_COST)
        self.price = MoneyEdit(fmt, S.FIELD_PRICE)
        self.stock = QSpinBox()
        self.stock.setRange(0, MAX_QTY)
        self.min_stock = QSpinBox()
        self.min_stock.setRange(0, MAX_QTY)

        form = QFormLayout()
        form.addRow(S.LBL_NAME, self.name)
        form.addRow(S.LBL_SKU, self.sku)
        form.addRow(S.LBL_CATEGORY, self.category)
        form.addRow(S.LBL_COST, self.cost)
        form.addRow(S.LBL_PRICE, self.price)
        form.addRow(S.LBL_STOCK_CURRENT if product else S.LBL_STOCK_INITIAL, self.stock)
        form.addRow(S.LBL_MIN_STOCK, self.min_stock)

        if product:
            self.name.setText(product.name)
            self.sku.setText(product.sku)
            self.category.setCurrentText(product.category)
            self.cost.set_value(product.cost_price)
            self.price.set_value(product.sale_price)
            self.stock.setValue(product.stock)
            self.stock.setEnabled(False)
            self.stock.setToolTip(S.PRODUCT_STOCK_HINT)
            self.min_stock.setValue(product.min_stock)

        buttons = QDialogButtonBox()
        ok = buttons.addButton(S.BTN_SAVE, QDialogButtonBox.ButtonRole.AcceptRole)
        ok.setObjectName("Primary")
        buttons.addButton(S.BTN_CANCEL, QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(buttons)

    def accept(self) -> None:
        try:
            cost, price = self.cost.value(), self.price.value()
            if self.product:
                self.ctx.products.update(
                    self.product.id, self.name.text(), self.sku.text(),
                    self.category.currentText(), cost, price, self.min_stock.value())
            else:
                self.ctx.products.create(
                    self.name.text(), self.sku.text(), self.category.currentText(),
                    cost, price, self.stock.value(), self.min_stock.value())
        except AppError as e:
            show_error(self, e)
            return
        except Exception as e:  # noqa: BLE001
            show_error(self, e)
            return
        super().accept()


class ProductsPage(BasePage):
    def __init__(self, ctx: AppContext):
        super().__init__(ctx, S.NAV_PRODUCTS)
        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(S.PRODUCTS_SEARCH)
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(320)
        self.search.textChanged.connect(lambda *_: self.refresh())
        self.btn_new = QPushButton(S.BTN_NEW_PRODUCT)
        self.btn_new.setObjectName("Primary")
        self.btn_edit = QPushButton(S.BTN_EDIT)
        self.btn_delete = QPushButton(S.BTN_DELETE)
        self.btn_delete.setObjectName("Danger")
        bar.addWidget(self.search)
        bar.addStretch(1)
        for b in (self.btn_new, self.btn_edit, self.btn_delete):
            bar.addWidget(b)
        self.body.addLayout(bar)

        self.table = make_table([S.COL_NAME, S.COL_SKU, S.COL_CATEGORY, S.COL_COST,
                                 S.COL_PRICE, S.COL_STOCK, S.COL_MIN_STOCK], stretch=0)
        self.body.addWidget(self.table, 1)

        self.btn_new.clicked.connect(self.on_new)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        self.table.doubleClicked.connect(lambda *_: self.on_edit())

    def refresh(self) -> None:
        fmt = self.ctx.currency
        products = self.ctx.products.list(self.search.text())
        rows = []
        for p in products:
            cells = [
                SortItem(p.name), SortItem(p.sku), SortItem(p.category),
                SortItem(fmt.format(p.cost_price), p.cost_price, RIGHT),
                SortItem(fmt.format(p.sale_price), p.sale_price, RIGHT),
                SortItem(str(p.stock), p.stock, RIGHT),
                SortItem(str(p.min_stock), p.min_stock, RIGHT),
            ]
            if p.is_low_stock:
                paint_row(cells)
            rows.append(cells)
        fill_table(self.table, rows, [p.id for p in products])

    @guarded
    def on_new(self) -> None:
        if ProductDialog(self.ctx, parent=self).exec():
            self.refresh()

    @guarded
    def on_edit(self) -> None:
        pid = selected_id(self.table)
        if pid is None:
            show_info(self, S.MSG_SELECT_PRODUCT)
            return
        if ProductDialog(self.ctx, self.ctx.products.get(pid), parent=self).exec():
            self.refresh()

    @guarded
    def on_delete(self) -> None:
        pid = selected_id(self.table)
        if pid is None:
            show_info(self, S.MSG_SELECT_PRODUCT)
            return
        p = self.ctx.products.get(pid)
        if not confirm(self, S.CONFIRM_DELETE_PRODUCT.format(name=p.name), S.BTN_DELETE):
            return
        result = self.ctx.products.delete(pid)
        if result == "archived":
            show_info(self, S.MSG_PRODUCT_ARCHIVED.format(name=p.name))
        self.refresh()
