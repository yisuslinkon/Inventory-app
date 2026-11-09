"""Pruebas de humo de la interfaz (se omiten si PySide6 no está instalado)."""
import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from inventory_app.context import AppContext  # noqa: E402
from inventory_app.ui.main_window import MainWindow  # noqa: E402
from inventory_app.ui.pages.products import ProductDialog  # noqa: E402
from inventory_app.ui.pages.sales import SalesPage  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def ctx(tmp_path):
    c = AppContext(tmp_path / "ui.db")
    yield c
    c.db.close()


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """Los diálogos modales bloquearían la prueba: los informativos se ignoran y los de error fallan."""
    def fail(_parent, error):
        raise AssertionError(f"Se mostró un diálogo de error: {error}")

    monkeypatch.setattr("inventory_app.ui.widgets.dialogs.show_error", fail)
    monkeypatch.setattr("inventory_app.ui.pages.sales.show_info", lambda *a, **k: None)
    monkeypatch.setattr("inventory_app.ui.pages.inventory.show_info", lambda *a, **k: None)


def test_every_page_refreshes(app, ctx):
    pid = ctx.products.create("Taza", "TAZ-1", "Hogar", 3000, 9000, stock=5, min_stock=5)
    ctx.sales.create_sale([(pid, 1)])
    window = MainWindow(ctx)
    for row in range(window.stack.count()):
        window.sidebar.setCurrentRow(row)
    window.close()


def test_product_dialog_creates_product(app, ctx):
    dlg = ProductDialog(ctx)
    dlg.name.setText("Taza")
    dlg.sku.setText("TAZ-1")
    dlg.category.setCurrentText("Hogar")
    dlg.cost.setText("3.000")
    dlg.price.setText("9000")
    dlg.stock.setValue(5)
    dlg.min_stock.setValue(2)
    dlg.accept()
    p = ctx.products.list()[0]
    assert (p.name, p.cost_price, p.sale_price, p.stock) == ("Taza", 3000, 9000, 5)


def test_sale_flow_through_ui(app, ctx):
    pid = ctx.products.create("Taza", "TAZ-1", "", 3000, 9000, stock=5)
    page = SalesPage(ctx)
    page.refresh()
    page.picker.setCurrentIndex(0)
    page.qty.setValue(2)
    page.on_add()
    assert page.cart == {pid: 2}
    page.on_register()
    assert page.cart == {}
    assert ctx.products.get(pid).stock == 3
    assert len(ctx.sales.list()) == 1
