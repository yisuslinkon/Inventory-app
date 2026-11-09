from __future__ import annotations

from dataclasses import dataclass

from .. import strings as S
from ..db.connection import Database
from .errors import InsufficientStockError, NotFoundError, ValidationError
from .validation import as_int

ADJUST_KINDS = ("restock", "loss", "correction")


@dataclass(frozen=True)
class Movement:
    id: int
    product_id: int
    product_name: str
    sku: str
    type: str
    quantity: int
    stock_after: int
    note: str
    sale_id: int | None
    created_at: str


class InventoryService:
    def __init__(self, db: Database):
        self.db = db

    def adjust(self, product_id: int, kind: str, quantity, note: str = "") -> int:
        """Ajusta el stock y registra el movimiento. Devuelve el stock resultante.

        restock:    suma `quantity` (> 0)
        loss:       resta `quantity` (> 0); no puede dejar el stock negativo
        correction: `quantity` es el conteo real (>= 0); se calcula la diferencia
        """
        if kind not in ADJUST_KINDS:
            raise ValidationError(S.ERR_INVALID_ADJUST_KIND)
        if kind == "correction":
            quantity = as_int(quantity, S.FIELD_COUNT, minimum=0)
        else:
            quantity = as_int(quantity, S.FIELD_QUANTITY, positive=True)
        note = (note or "").strip()

        with self.db.transaction() as c:
            row = c.execute(
                "SELECT name, stock, is_active FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            if row is None:
                raise NotFoundError(S.ERR_PRODUCT_NOT_FOUND)
            if not row["is_active"]:
                raise ValidationError(S.ERR_PRODUCT_INACTIVE.format(name=row["name"]))
            stock = row["stock"]
            if kind == "restock":
                delta = quantity
            elif kind == "loss":
                if quantity > stock:
                    raise InsufficientStockError(S.ERR_INSUFFICIENT_STOCK.format(
                        name=row["name"], available=stock, requested=quantity))
                delta = -quantity
            else:
                delta = quantity - stock
                if delta == 0:
                    raise ValidationError(S.ERR_CORRECTION_NO_CHANGE)
            new_stock = stock + delta
            now = self.db.clock()
            c.execute("UPDATE products SET stock = ?, updated_at = ? WHERE id = ?",
                      (new_stock, now, product_id))
            c.execute(
                "INSERT INTO stock_movements(product_id, type, quantity, stock_after, note,"
                " created_at) VALUES (?,?,?,?,?,?)",
                (product_id, kind, delta, new_stock, note, now),
            )
            return new_stock

    def history(self, product_id: int | None = None, limit: int = 500) -> list[Movement]:
        sql = ("SELECT m.*, p.name AS product_name, p.sku AS sku FROM stock_movements m"
               " JOIN products p ON p.id = m.product_id")
        params: list = []
        if product_id is not None:
            sql += " WHERE m.product_id = ?"
            params.append(product_id)
        sql += " ORDER BY m.created_at DESC, m.id DESC LIMIT ?"
        params.append(limit)
        return [
            Movement(r["id"], r["product_id"], r["product_name"], r["sku"], r["type"],
                     r["quantity"], r["stock_after"], r["note"], r["sale_id"], r["created_at"])
            for r in self.db.conn.execute(sql, params)
        ]
