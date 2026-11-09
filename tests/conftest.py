import pytest

from inventory_app.db.connection import Database
from inventory_app.services.inventory import InventoryService
from inventory_app.services.products import ProductService
from inventory_app.services.sales import SaleService


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    d.clock = lambda: "2026-11-08 10:00:00"
    yield d
    d.close()


@pytest.fixture
def products(db):
    return ProductService(db)


@pytest.fixture
def inventory(db):
    return InventoryService(db)


@pytest.fixture
def sales(db):
    return SaleService(db)


@pytest.fixture
def two_products(products):
    """Camiseta (costo 20.000, venta 50.000, stock 10) y Gorra (5.000/12.000, stock 3)."""
    a = products.create("Camiseta", "CAM-001", "Ropa", 20_000, 50_000, stock=10, min_stock=2)
    b = products.create("Gorra", "GOR-001", "Ropa", 5_000, 12_000, stock=3, min_stock=3)
    return a, b
