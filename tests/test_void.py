import pytest

from inventory_app.services.errors import NotFoundError, ValidationError


def test_void_restores_stock_and_logs(sales, products, inventory, two_products):
    cam, gor = two_products
    sid = sales.create_sale([(cam, 4), (gor, 2)])
    sales.void_sale(sid, "cliente devolvió")
    assert products.get(cam).stock == 10 and products.get(gor).stock == 3
    s = sales.get(sid)
    assert s.status == "voided" and s.void_reason == "cliente devolvió" and s.voided_at
    m = inventory.history(cam)[0]
    assert (m.type, m.quantity, m.stock_after, m.sale_id) == ("void", 4, 10, sid)


def test_cannot_void_twice(sales, products, two_products):
    cam, _ = two_products
    sid = sales.create_sale([(cam, 1)])
    sales.void_sale(sid)
    with pytest.raises(ValidationError):
        sales.void_sale(sid)
    assert products.get(cam).stock == 10  # no se repone dos veces


def test_void_unknown_sale(sales):
    with pytest.raises(NotFoundError):
        sales.void_sale(12345)


def test_void_restores_stock_even_if_product_archived(sales, products, two_products):
    cam, _ = two_products
    sid = sales.create_sale([(cam, 2)])
    products.delete(cam)
    sales.void_sale(sid)
    assert products.get(cam, include_inactive=True).stock == 10


def test_list_excludes_voided_when_asked(sales, two_products):
    cam, _ = two_products
    a = sales.create_sale([(cam, 1)])
    sales.create_sale([(cam, 1)])
    sales.void_sale(a)
    assert len(sales.list()) == 2
    assert len(sales.list(include_voided=False)) == 1
