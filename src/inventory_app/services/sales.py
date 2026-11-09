from __future__ import annotations

from dataclasses import dataclass

from .. import strings as S
from ..db.connection import Database
from .errors import InsufficientStockError, NotFoundError, ValidationError
from .validation import as_int


@dataclass(frozen=True)
class SaleItem:
    product_id: int
    product_name: str
    sku: str
    quantity: int
    unit_price: int
    unit_cost: int

    @property
    def line_total(self) -> int:
        return self.quantity * self.unit_price

    @property
    def line_profit(self) -> int:
        return self.quantity * (self.unit_price - self.unit_cost)


@dataclass(frozen=True)
class Sale:
    id: int
    created_at: str
    total: int
    status: str
    voided_at: str | None
    void_reason: str
    note: str
    items: tuple[SaleItem, ...] = ()

    @property
    def profit(self) -> int:
        return sum(i.line_profit for i in self.items)

    @property
    def units(self) -> int:
        return sum(i.quantity for i in self.items)


class SaleService:
    def __init__(self, db: Database):
        self.db = db

    def create_sale(self, lines, note: str = "") -> int:
        """Registra una venta. `lines` = iterable de (product_id, quantity).

        Todo ocurre en una sola transacción: si cualquier línea falla (por ejemplo
        stock insuficiente) no se guarda nada y el stock queda intacto.
        """
        merged: dict[int, int] = {}
        for product_id, qty in lines:
            qty = as_int(qty, S.FIELD_QUANTITY, positive=True)
            merged[product_id] = merged.get(product_id, 0) + qty
        if not merged:
            raise ValidationError(S.ERR_NO_ITEMS)
        note = (note or "").strip()

        with self.db.transaction() as c:
            now = self.db.clock()
            priced = []
            for product_id, qty in merged.items():
                p = c.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
                if p is None:
                    raise NotFoundError(S.ERR_PRODUCT_NOT_FOUND)
                if not p["is_active"]:
                    raise ValidationError(S.ERR_PRODUCT_INACTIVE.format(name=p["name"]))
                if p["stock"] < qty:
                    raise InsufficientStockError(S.ERR_INSUFFICIENT_STOCK.format(
                        name=p["name"], available=p["stock"], requested=qty))
                priced.append((p, qty))

            total = sum(qty * p["sale_price"] for p, qty in priced)
            sale_id = c.execute(
                "INSERT INTO sales(created_at, total, note) VALUES (?,?,?)", (now, total, note)
            ).lastrowid
            for p, qty in priced:
                c.execute(
                    "INSERT INTO sale_items(sale_id, product_id, quantity, unit_price, unit_cost)"
                    " VALUES (?,?,?,?,?)",
                    (sale_id, p["id"], qty, p["sale_price"], p["cost_price"]),
                )
                new_stock = p["stock"] - qty
                cur = c.execute(
                    "UPDATE products SET stock = ?, updated_at = ? WHERE id = ? AND stock >= ?",
                    (new_stock, now, p["id"], qty),
                )
                if cur.rowcount != 1:  # defensa extra ante cambios concurrentes
                    raise InsufficientStockError(S.ERR_INSUFFICIENT_STOCK.format(
                        name=p["name"], available=p["stock"], requested=qty))
                c.execute(
                    "INSERT INTO stock_movements(product_id, type, quantity, stock_after, note,"
                    " sale_id, created_at) VALUES (?, 'sale', ?, ?, '', ?, ?)",
                    (p["id"], -qty, new_stock, sale_id, now),
                )
            return sale_id

    def void_sale(self, sale_id: int, reason: str = "") -> None:
        reason = (reason or "").strip()
        with self.db.transaction() as c:
            sale = c.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
            if sale is None:
                raise NotFoundError(S.ERR_SALE_NOT_FOUND)
            if sale["status"] == "voided":
                raise ValidationError(S.ERR_SALE_ALREADY_VOIDED.format(id=sale_id))
            now = self.db.clock()
            c.execute(
                "UPDATE sales SET status='voided', voided_at=?, void_reason=? WHERE id=?",
                (now, reason, sale_id),
            )
            items = c.execute(
                "SELECT product_id, quantity FROM sale_items WHERE sale_id = ?", (sale_id,)
            ).fetchall()
            for it in items:
                stock = c.execute("SELECT stock FROM products WHERE id = ?",
                                  (it["product_id"],)).fetchone()["stock"]
                new_stock = stock + it["quantity"]
                c.execute("UPDATE products SET stock = ?, updated_at = ? WHERE id = ?",
                          (new_stock, now, it["product_id"]))
                c.execute(
                    "INSERT INTO stock_movements(product_id, type, quantity, stock_after, note,"
                    " sale_id, created_at) VALUES (?, 'void', ?, ?, ?, ?, ?)",
                    (it["product_id"], it["quantity"], new_stock, reason, sale_id, now),
                )

    def get(self, sale_id: int) -> Sale:
        r = self.db.conn.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
        if r is None:
            raise NotFoundError(S.ERR_SALE_NOT_FOUND)
        return self._build(r)

    def list(self, start: str | None = None, end: str | None = None,
             include_voided: bool = True, limit: int = 1000) -> list[Sale]:
        """Lista ventas. `start`/`end` son 'YYYY-MM-DD' (ambos inclusive)."""
        sql, params = "SELECT * FROM sales WHERE 1=1", []
        if start:
            sql += " AND created_at >= ?"
            params.append(f"{start} 00:00:00")
        if end:
            sql += " AND created_at <= ?"
            params.append(f"{end} 23:59:59")
        if not include_voided:
            sql += " AND status = 'completed'"
        sql += " ORDER BY created_at DESC, id DESC LIMIT ?"
        params.append(limit)
        return [self._build(r) for r in self.db.conn.execute(sql, params)]

    def _build(self, r) -> Sale:
        items = tuple(
            SaleItem(i["product_id"], i["name"], i["sku"], i["quantity"],
                     i["unit_price"], i["unit_cost"])
            for i in self.db.conn.execute(
                "SELECT si.*, p.name, p.sku FROM sale_items si"
                " JOIN products p ON p.id = si.product_id WHERE si.sale_id = ? ORDER BY si.id",
                (r["id"],))
        )
        return Sale(r["id"], r["created_at"], r["total"], r["status"], r["voided_at"],
                    r["void_reason"], r["note"], items)
