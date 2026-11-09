from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from .. import strings as S
from ..db.connection import Database
from .errors import DuplicateSkuError, NotFoundError
from .validation import as_int, required_text


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    sku: str
    category: str
    cost_price: int
    sale_price: int
    stock: int
    min_stock: int
    is_active: bool

    @property
    def is_low_stock(self) -> bool:
        return self.stock <= self.min_stock


def _row(r: sqlite3.Row) -> Product:
    return Product(
        id=r["id"], name=r["name"], sku=r["sku"], category=r["category"],
        cost_price=r["cost_price"], sale_price=r["sale_price"], stock=r["stock"],
        min_stock=r["min_stock"], is_active=bool(r["is_active"]),
    )


def _like(text: str) -> str:
    esc = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{esc}%"


class ProductService:
    def __init__(self, db: Database):
        self.db = db

    # -------------------------------------------------------------- lectura
    def get(self, product_id: int, *, include_inactive: bool = False) -> Product:
        r = self.db.conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if r is None or (not r["is_active"] and not include_inactive):
            raise NotFoundError(S.ERR_PRODUCT_NOT_FOUND)
        return _row(r)

    def list(self, search: str = "", *, low_stock_only: bool = False) -> list[Product]:
        sql = "SELECT * FROM products WHERE is_active = 1"
        params: list = []
        search = (search or "").strip()
        if search:
            sql += (" AND (name LIKE ? ESCAPE '\\' OR sku LIKE ? ESCAPE '\\'"
                    " OR category LIKE ? ESCAPE '\\')")
            params += [_like(search)] * 3
        if low_stock_only:
            sql += " AND stock <= min_stock"
        sql += " ORDER BY name COLLATE NOCASE"
        return [_row(r) for r in self.db.conn.execute(sql, params)]

    def categories(self) -> list[str]:
        rows = self.db.conn.execute(
            "SELECT DISTINCT category FROM products WHERE is_active = 1 AND category != '' "
            "ORDER BY category COLLATE NOCASE"
        )
        return [r["category"] for r in rows]

    # ------------------------------------------------------------ escritura
    def _validate(self, name, sku, category, cost_price, sale_price, min_stock):
        return (
            required_text(name, S.ERR_NAME_REQUIRED),
            required_text(sku, S.ERR_SKU_REQUIRED),
            (category or "").strip(),
            as_int(cost_price, S.FIELD_COST, minimum=0),
            as_int(sale_price, S.FIELD_PRICE, minimum=0),
            as_int(min_stock, S.FIELD_MIN_STOCK, minimum=0),
        )

    def create(self, name, sku, category, cost_price, sale_price, stock=0, min_stock=0) -> int:
        name, sku, category, cost, price, min_stock = self._validate(
            name, sku, category, cost_price, sale_price, min_stock)
        stock = as_int(stock, S.FIELD_STOCK, minimum=0)
        now = self.db.clock()
        try:
            with self.db.transaction() as c:
                cur = c.execute(
                    "INSERT INTO products(name, sku, category, cost_price, sale_price, stock,"
                    " min_stock, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                    (name, sku, category, cost, price, stock, min_stock, now, now),
                )
                pid = cur.lastrowid
                if stock > 0:
                    c.execute(
                        "INSERT INTO stock_movements(product_id, type, quantity, stock_after,"
                        " note, created_at) VALUES (?, 'initial', ?, ?, '', ?)",
                        (pid, stock, stock, now),
                    )
                return pid
        except sqlite3.IntegrityError as e:
            if "sku" in str(e).lower():
                raise DuplicateSkuError(S.ERR_SKU_DUPLICATE.format(sku=sku)) from e
            raise

    def update(self, product_id, name, sku, category, cost_price, sale_price, min_stock) -> None:
        """Edita datos del producto. El stock solo cambia con ajustes de inventario."""
        name, sku, category, cost, price, min_stock = self._validate(
            name, sku, category, cost_price, sale_price, min_stock)
        self.get(product_id)
        try:
            with self.db.transaction() as c:
                c.execute(
                    "UPDATE products SET name=?, sku=?, category=?, cost_price=?, sale_price=?,"
                    " min_stock=?, updated_at=? WHERE id=?",
                    (name, sku, category, cost, price, min_stock, self.db.clock(), product_id),
                )
        except sqlite3.IntegrityError as e:
            if "sku" in str(e).lower():
                raise DuplicateSkuError(S.ERR_SKU_DUPLICATE.format(sku=sku)) from e
            raise

    def delete(self, product_id: int) -> str:
        """Borra el producto si no tiene historial; si lo tiene, lo archiva.

        Devuelve 'deleted' o 'archived'.
        """
        self.get(product_id)
        with self.db.transaction() as c:
            used = c.execute(
                "SELECT (SELECT COUNT(*) FROM sale_items WHERE product_id = ?)"
                " + (SELECT COUNT(*) FROM stock_movements WHERE product_id = ? AND type != 'initial')",
                (product_id, product_id),
            ).fetchone()[0]
            if used:
                c.execute("UPDATE products SET is_active = 0, updated_at = ? WHERE id = ?",
                          (self.db.clock(), product_id))
                return "archived"
            c.execute("DELETE FROM stock_movements WHERE product_id = ?", (product_id,))
            c.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return "deleted"
