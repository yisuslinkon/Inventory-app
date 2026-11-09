from inventory_app.services.dashboard import DashboardService, month_bounds


def sell_on(db, sales, date_str, lines):
    db.clock = lambda: f"{date_str} 12:00:00"
    return sales.create_sale(lines)


def test_month_bounds_december():
    assert month_bounds(2026, 12) == ("2026-12-01 00:00:00", "2027-01-01 00:00:00")


def test_month_summary(db, sales, products, two_products):
    cam, gor = two_products
    sell_on(db, sales, "2026-11-03", [(cam, 2)])
    sell_on(db, sales, "2026-11-30", [(gor, 1)])
    sell_on(db, sales, "2026-10-31", [(cam, 1)])  # otro mes
    d = DashboardService(db)
    s = d.month_summary(2026, 11)
    assert (s.revenue, s.units, s.profit) == (112_000, 3, 67_000)


def test_voided_sales_excluded(db, sales, two_products):
    cam, _ = two_products
    sid = sell_on(db, sales, "2026-11-03", [(cam, 2)])
    sales.void_sale(sid)
    s = DashboardService(db).month_summary(2026, 11)
    assert (s.revenue, s.units, s.profit) == (0, 0, 0)


def test_monthly_sales_12_months_fills_zeros(db, sales, products, two_products):
    cam, _ = two_products
    products.update(cam, "Camiseta", "CAM-001", "Ropa", 20_000, 50_000, 2)
    sell_on(db, sales, "2026-11-03", [(cam, 1)])
    sell_on(db, sales, "2025-12-15", [(cam, 2)])   # primer mes de la ventana
    sell_on(db, sales, "2025-11-15", [(cam, 1)])   # fuera de la ventana
    pts = DashboardService(db).monthly_sales(2026, 11)
    assert len(pts) == 12
    assert pts[0].label == "2025-12" and pts[0].revenue == 100_000
    assert pts[-1].label == "2026-11" and pts[-1].revenue == 50_000
    assert sum(p.revenue for p in pts[1:-1]) == 0


def test_top_products_limit_and_order(db, sales, products):
    ids = [products.create(f"P{i}", f"S{i}", "", 1, 10, stock=100) for i in range(7)]
    for i, pid in enumerate(ids):
        sell_on(db, sales, "2026-11-05", [(pid, i + 1)])
    top = DashboardService(db).top_products(2026, 11)
    assert [t.name for t in top] == ["P6", "P5", "P4", "P3", "P2"]
    assert top[0].units == 7 and top[0].revenue == 70


def test_low_stock(db, sales, two_products):
    cam, gor = two_products
    d = DashboardService(db)
    assert [p.name for p in d.low_stock()] == ["Gorra"]
    sales.create_sale([(cam, 8)])  # stock 2 <= mínimo 2
    assert [p.name for p in d.low_stock()] == ["Camiseta", "Gorra"]
