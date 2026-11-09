from __future__ import annotations

from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QInputDialog, QLabel, QLineEdit, QPushButton,
                               QSpinBox, QTabWidget, QVBoxLayout, QWidget)

from ... import strings as S
from ...context import AppContext
from ...services.errors import InsufficientStockError
from ..util import display_dt
from ..widgets.dialogs import confirm, guarded, show_error, show_info
from ..widgets.product_picker import ProductPicker
from ..widgets.tables import (BAD, MUTED, RIGHT, SortItem, fill_table, make_table, selected_id,
                              tint)
from .base import BasePage, make_card

MAX_QTY = 1_000_000


class SalesPage(BasePage):
    def __init__(self, ctx: AppContext):
        super().__init__(ctx, S.NAV_SALES)
        self.cart: dict[int, int] = {}
        tabs = QTabWidget()
        tabs.addTab(self._build_new_sale(), S.TAB_NEW_SALE)
        tabs.addTab(self._build_history(), S.TAB_SALES_HISTORY)
        tabs.currentChanged.connect(lambda *_: self.refresh())
        self.tabs = tabs
        self.body.addWidget(tabs, 1)

    # ---------------------------------------------------------- nueva venta
    def _build_new_sale(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(12)

        card, cl = make_card()
        row = QHBoxLayout()
        self.picker = ProductPicker(show_stock=True)
        self.qty = QSpinBox()
        self.qty.setRange(1, MAX_QTY)
        self.qty.setValue(1)
        self.btn_add = QPushButton(S.BTN_ADD_TO_SALE)
        self.btn_add.setObjectName("Primary")
        row.addWidget(QLabel(S.LBL_PRODUCT))
        row.addWidget(self.picker, 1)
        row.addWidget(QLabel(S.LBL_QUANTITY))
        row.addWidget(self.qty)
        row.addWidget(self.btn_add)
        cl.addLayout(row)
        lay.addWidget(card)

        self.cart_table = make_table([S.COL_PRODUCT, S.COL_QUANTITY, S.COL_PRICE,
                                      S.COL_SUBTOTAL, ""], stretch=0)
        self.cart_table.setSortingEnabled(False)
        lay.addWidget(self.cart_table, 1)

        foot = QHBoxLayout()
        self.note = QLineEdit()
        self.note.setPlaceholderText(S.LBL_NOTE_OPTIONAL)
        self.total_label = QLabel("")
        f = self.total_label.font()
        f.setPointSizeF(f.pointSizeF() * 1.6)
        f.setBold(True)
        self.total_label.setFont(f)
        self.btn_clear = QPushButton(S.BTN_CLEAR_SALE)
        self.btn_register = QPushButton(S.BTN_REGISTER_SALE)
        self.btn_register.setObjectName("Primary")
        foot.addWidget(self.note, 1)
        foot.addSpacing(16)
        foot.addWidget(self.total_label)
        foot.addSpacing(16)
        foot.addWidget(self.btn_clear)
        foot.addWidget(self.btn_register)
        lay.addLayout(foot)

        self.btn_add.clicked.connect(self.on_add)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_register.clicked.connect(self.on_register)
        return w

    # ------------------------------------------------------------ historial
    def _build_history(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(12)
        bar = QHBoxLayout()
        bar.addWidget(QLabel(S.LBL_LAST_SALES))
        bar.addStretch(1)
        self.btn_void = QPushButton(S.BTN_VOID_SALE)
        self.btn_void.setObjectName("Danger")
        bar.addWidget(self.btn_void)
        lay.addLayout(bar)
        self.sales_table = make_table([S.COL_SALE_NO, S.COL_DATE, S.COL_DETAIL, S.COL_UNITS,
                                       S.COL_TOTAL, S.COL_PROFIT, S.COL_STATUS], stretch=2)
        lay.addWidget(self.sales_table, 1)
        self.btn_void.clicked.connect(self.on_void)
        return w

    # ------------------------------------------------------------- refresco
    def refresh(self) -> None:
        self.picker.load(self.ctx.products.list())
        # Quitar del carrito productos que ya no existan
        for pid in list(self.cart):
            try:
                self.ctx.products.get(pid)
            except Exception:  # noqa: BLE001
                self.cart.pop(pid, None)
        self._render_cart()
        self._render_history()

    def _render_cart(self) -> None:
        fmt = self.ctx.currency
        t = self.cart_table
        t.setRowCount(len(self.cart))
        total = 0
        for r, (pid, qty) in enumerate(self.cart.items()):
            p = self.ctx.products.get(pid)
            sub = qty * p.sale_price
            total += sub
            t.setItem(r, 0, SortItem(f"{p.name} — {p.sku}"))
            t.setItem(r, 1, SortItem(str(qty), qty, RIGHT))
            t.setItem(r, 2, SortItem(fmt.format(p.sale_price), p.sale_price, RIGHT))
            t.setItem(r, 3, SortItem(fmt.format(sub), sub, RIGHT))
            btn = QPushButton(S.BTN_REMOVE)
            btn.clicked.connect(partial(self._remove, pid))
            t.setCellWidget(r, 4, btn)
        self.total_label.setText(f"{S.LBL_TOTAL}: {fmt.format(total)}")
        self.btn_register.setEnabled(bool(self.cart))
        self.btn_clear.setEnabled(bool(self.cart))

    def _render_history(self) -> None:
        fmt = self.ctx.currency
        sales = self.ctx.sales.list(limit=300)
        rows = []
        for s in sales:
            detail = ", ".join(f"{i.quantity}× {i.product_name}" for i in s.items)
            voided = s.status == "voided"
            cells = [
                SortItem(f"#{s.id}", s.id, RIGHT),
                SortItem(display_dt(s.created_at), s.created_at),
                SortItem(detail),
                SortItem(str(s.units), s.units, RIGHT),
                SortItem(fmt.format(s.total), s.total, RIGHT),
                SortItem(fmt.format(s.profit), s.profit, RIGHT),
                SortItem(S.SALE_STATUS_LABELS[s.status]),
            ]
            if voided:
                for c in cells:
                    tint(c, MUTED)
                tint(cells[-1], BAD)
            rows.append(cells)
        fill_table(self.sales_table, rows, [s.id for s in sales])

    # --------------------------------------------------------------- acciones
    def _remove(self, pid: int) -> None:
        self.cart.pop(pid, None)
        self._render_cart()

    @guarded
    def on_add(self) -> None:
        pid = self.picker.require_id()
        p = self.ctx.products.get(pid)
        wanted = self.cart.get(pid, 0) + self.qty.value()
        if wanted > p.stock:
            raise InsufficientStockError(S.ERR_INSUFFICIENT_STOCK.format(
                name=p.name, available=p.stock, requested=wanted))
        self.cart[pid] = wanted
        self.qty.setValue(1)
        self.picker.setCurrentIndex(-1)
        self.picker.setEditText("")
        self.picker.setFocus(Qt.FocusReason.OtherFocusReason)
        self._render_cart()

    @guarded
    def on_clear(self) -> None:
        self.cart.clear()
        self._render_cart()

    @guarded
    def on_register(self) -> None:
        fmt = self.ctx.currency
        sale_id = self.ctx.sales.create_sale(list(self.cart.items()), self.note.text())
        total = self.ctx.sales.get(sale_id).total
        self.cart.clear()
        self.note.clear()
        self.refresh()
        show_info(self, S.MSG_SALE_OK.format(id=sale_id, total=fmt.format(total)))

    @guarded
    def on_void(self) -> None:
        sale_id = selected_id(self.sales_table)
        if sale_id is None:
            show_info(self, S.MSG_SELECT_SALE)
            return
        sale = self.ctx.sales.get(sale_id)
        if sale.status == "voided":
            show_error(self, S.ERR_SALE_ALREADY_VOIDED.format(id=sale_id))
            return
        if not confirm(self, S.CONFIRM_VOID_SALE.format(id=sale_id), S.BTN_VOID_SALE):
            return
        reason, ok = QInputDialog.getText(self, S.DLG_VOID_REASON_TITLE, S.DLG_VOID_REASON_LABEL)
        if not ok:
            return
        self.ctx.sales.void_sale(sale_id, reason)
        self.refresh()
        show_info(self, S.MSG_SALE_VOIDED.format(id=sale_id))
