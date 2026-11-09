import pytest

from inventory_app.services.errors import DuplicateSkuError, NotFoundError, ValidationError


def test_create_and_get(products):
    pid = products.create("Taza", "TAZ-1", "Hogar", 3_000, 9_000, stock=5, min_stock=1)
    p = products.get(pid)
    assert (p.name, p.sku, p.stock, p.cost_price, p.sale_price) == ("Taza", "TAZ-1", 5, 3000, 9000)


def test_initial_stock_creates_movement(products, inventory):
    pid = products.create("Taza", "TAZ-1", "", 1, 2, stock=5)
    hist = inventory.history(pid)
    assert len(hist) == 1 and hist[0].type == "initial" and hist[0].stock_after == 5


@pytest.mark.parametrize("kwargs", [
    dict(name="  ", sku="X"), dict(name="A", sku=""),
    dict(name="A", sku="X", cost_price=-1), dict(name="A", sku="X", sale_price=-5),
    dict(name="A", sku="X", cost_price=1.5), dict(name="A", sku="X", stock=-1),
    dict(name="A", sku="X", min_stock=-1), dict(name="A", sku="X", cost_price="abc"),
])
def test_validation(products, kwargs):
    base = dict(name="A", sku="X", category="", cost_price=1, sale_price=2)
    base.update(kwargs)
    with pytest.raises(ValidationError):
        products.create(**base)


def test_duplicate_sku_case_insensitive(products):
    products.create("A", "sku-1", "", 1, 2)
    with pytest.raises(DuplicateSkuError):
        products.create("B", "SKU-1", "", 1, 2)


def test_update_keeps_stock_and_checks_sku(products):
    a = products.create("A", "A-1", "", 1, 2, stock=7)
    products.create("B", "B-1", "", 1, 2)
    products.update(a, "A nuevo", "A-1", "Cat", 10, 20, 3)
    p = products.get(a)
    assert (p.name, p.cost_price, p.sale_price, p.min_stock, p.stock) == ("A nuevo", 10, 20, 3, 7)
    with pytest.raises(DuplicateSkuError):
        products.update(a, "A", "B-1", "", 1, 2, 0)


def test_search_and_low_stock(products, two_products):
    assert [p.name for p in products.list("cam")] == ["Camiseta"]
    assert [p.name for p in products.list("GOR-0")] == ["Gorra"]
    assert [p.name for p in products.list(low_stock_only=True)] == ["Gorra"]  # 3 <= 3
    assert products.list("100%") == []  # el % no actúa como comodín


def test_delete_without_history_removes(products, db):
    pid = products.create("A", "A-1", "", 1, 2, stock=4)
    assert products.delete(pid) == "deleted"
    with pytest.raises(NotFoundError):
        products.get(pid)
    assert db.conn.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0] == 0


def test_delete_with_history_archives_and_frees_sku(products, sales, two_products):
    cam, _ = two_products
    sales.create_sale([(cam, 1)])
    assert products.delete(cam) == "archived"
    assert all(p.id != cam for p in products.list())
    assert products.get(cam, include_inactive=True).is_active is False
    products.create("Camiseta nueva", "CAM-001", "", 1, 2)  # SKU reutilizable
