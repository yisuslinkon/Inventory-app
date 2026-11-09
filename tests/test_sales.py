import pytest

from inventory_app.services.errors import InsufficientStockError, NotFoundError, ValidationError


def stock(products, pid):
    return products.get(pid, include_inactive=True).stock


def test_sale_decreases_stock_and_totals(sales, products, two_products):
    cam, gor = two_products
    sid = sales.create_sale([(cam, 2), (gor, 1)])
    s = sales.get(sid)
    assert s.total == 2 * 50_000 + 12_000
    assert s.profit == 2 * 30_000 + 7_000
    assert s.units == 3 and s.status == "completed"
    assert stock(products, cam) == 8 and stock(products, gor) == 2


def test_sale_records_movements(sales, inventory, two_products):
    cam, _ = two_products
    sid = sales.create_sale([(cam, 3)])
    m = inventory.history(cam)[0]
    assert (m.type, m.quantity, m.stock_after, m.sale_id) == ("sale", -3, 7, sid)


def test_insufficient_stock_blocks_whole_sale(sales, products, two_products):
    cam, gor = two_products
    with pytest.raises(InsufficientStockError) as e:
        sales.create_sale([(cam, 2), (gor, 4)])  # solo hay 3 gorras
    assert "Gorra" in str(e.value) and "3" in str(e.value)
    assert stock(products, cam) == 10 and stock(products, gor) == 3  # nada cambió
    assert sales.list() == []


def test_can_sell_exact_stock(sales, products, two_products):
    cam, _ = two_products
    sales.create_sale([(cam, 10)])
    assert stock(products, cam) == 0
    with pytest.raises(InsufficientStockError):
        sales.create_sale([(cam, 1)])


def test_duplicate_lines_are_merged_for_stock_check(sales, products, two_products):
    _, gor = two_products
    with pytest.raises(InsufficientStockError):
        sales.create_sale([(gor, 2), (gor, 2)])
    sid = sales.create_sale([(gor, 1), (gor, 2)])
    assert len(sales.get(sid).items) == 1 and sales.get(sid).items[0].quantity == 3


@pytest.mark.parametrize("lines", [[], [(1, 0)], [(1, -2)], [(1, "x")], [(1, 1.5)]])
def test_invalid_lines(sales, two_products, lines):
    with pytest.raises(ValidationError):
        sales.create_sale(lines)


def test_unknown_or_archived_product(sales, products, two_products):
    cam, _ = two_products
    with pytest.raises(NotFoundError):
        sales.create_sale([(9999, 1)])
    sales.create_sale([(cam, 1)])
    products.delete(cam)  # archivado
    with pytest.raises(ValidationError):
        sales.create_sale([(cam, 1)])


def test_price_snapshot_survives_price_change(sales, products, two_products):
    cam, _ = two_products
    sid = sales.create_sale([(cam, 1)])
    products.update(cam, "Camiseta", "CAM-001", "Ropa", 99_000, 150_000, 2)
    s = sales.get(sid)
    assert s.items[0].unit_price == 50_000 and s.items[0].unit_cost == 20_000
    assert s.profit == 30_000


def test_failed_sale_rolls_back_atomically(db, sales, products, two_products):
    """Si algo falla a mitad de la venta, no queda venta, ítems ni cambios de stock."""
    cam, gor = two_products
    # Forzamos un fallo después de insertar la primera línea: un CHECK imposible.
    db.conn.execute(
        "CREATE TRIGGER fail_second BEFORE INSERT ON sale_items "
        "WHEN (SELECT COUNT(*) FROM sale_items WHERE sale_id = NEW.sale_id) >= 1 "
        "BEGIN SELECT RAISE(ABORT, 'fallo simulado'); END")
    with pytest.raises(Exception):
        sales.create_sale([(cam, 1), (gor, 1)])
    assert stock(products, cam) == 10 and stock(products, gor) == 3
    assert db.conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0
    assert db.conn.execute("SELECT COUNT(*) FROM sale_items").fetchone()[0] == 0
    assert db.conn.execute("SELECT COUNT(*) FROM stock_movements WHERE type='sale'").fetchone()[0] == 0
    assert not db.conn.in_transaction
