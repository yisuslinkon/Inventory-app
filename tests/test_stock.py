import pytest

from inventory_app.services.errors import InsufficientStockError, NotFoundError, ValidationError


def test_restock(inventory, products, two_products):
    cam, _ = two_products
    assert inventory.adjust(cam, "restock", 5, "compra") == 15
    assert products.get(cam).stock == 15
    m = inventory.history(cam)[0]
    assert (m.type, m.quantity, m.stock_after, m.note) == ("restock", 5, 15, "compra")


def test_loss(inventory, products, two_products):
    cam, _ = two_products
    assert inventory.adjust(cam, "loss", 4) == 6
    assert inventory.history(cam)[0].quantity == -4


def test_loss_cannot_go_negative(inventory, products, two_products):
    cam, _ = two_products
    with pytest.raises(InsufficientStockError):
        inventory.adjust(cam, "loss", 11)
    assert products.get(cam).stock == 10
    assert len(inventory.history(cam)) == 1  # solo el stock inicial


def test_correction_sets_absolute_count(inventory, products, two_products):
    cam, _ = two_products
    assert inventory.adjust(cam, "correction", 7) == 7
    m = inventory.history(cam)[0]
    assert (m.type, m.quantity, m.stock_after) == ("correction", -3, 7)
    assert inventory.adjust(cam, "correction", 0) == 0


def test_correction_same_count_rejected(inventory, two_products):
    with pytest.raises(ValidationError):
        inventory.adjust(two_products[0], "correction", 10)


@pytest.mark.parametrize("kind,qty", [("restock", 0), ("restock", -1), ("loss", 0),
                                      ("correction", -1), ("restock", "x"), ("restock", 1.5)])
def test_invalid_quantities(inventory, two_products, kind, qty):
    with pytest.raises(ValidationError):
        inventory.adjust(two_products[0], kind, qty)


def test_invalid_kind_and_missing_product(inventory, two_products):
    with pytest.raises(ValidationError):
        inventory.adjust(two_products[0], "regalo", 1)
    with pytest.raises(NotFoundError):
        inventory.adjust(9999, "restock", 1)


def test_history_order_and_filter(inventory, two_products):
    cam, gor = two_products
    inventory.adjust(cam, "restock", 1)
    inventory.adjust(gor, "loss", 1)
    assert [m.type for m in inventory.history(cam)] == ["restock", "initial"]
    assert len(inventory.history()) == 4
