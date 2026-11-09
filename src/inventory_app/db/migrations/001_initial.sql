CREATE TABLE products (
  id          INTEGER PRIMARY KEY,
  name        TEXT    NOT NULL CHECK (length(trim(name)) > 0),
  sku         TEXT    NOT NULL CHECK (length(trim(sku)) > 0),
  category    TEXT    NOT NULL DEFAULT '',
  cost_price  INTEGER NOT NULL CHECK (cost_price >= 0),
  sale_price  INTEGER NOT NULL CHECK (sale_price >= 0),
  stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
  min_stock   INTEGER NOT NULL DEFAULT 0 CHECK (min_stock >= 0),
  is_active   INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
  created_at  TEXT    NOT NULL,
  updated_at  TEXT    NOT NULL
);
CREATE UNIQUE INDEX ux_products_sku ON products(sku COLLATE NOCASE) WHERE is_active = 1;
CREATE INDEX ix_products_name ON products(name);

CREATE TABLE sales (
  id          INTEGER PRIMARY KEY,
  created_at  TEXT    NOT NULL,
  total       INTEGER NOT NULL CHECK (total >= 0),
  status      TEXT    NOT NULL DEFAULT 'completed' CHECK (status IN ('completed', 'voided')),
  voided_at   TEXT,
  void_reason TEXT    NOT NULL DEFAULT '',
  note        TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX ix_sales_created ON sales(created_at);

CREATE TABLE sale_items (
  id          INTEGER PRIMARY KEY,
  sale_id     INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
  product_id  INTEGER NOT NULL REFERENCES products(id),
  quantity    INTEGER NOT NULL CHECK (quantity > 0),
  unit_price  INTEGER NOT NULL CHECK (unit_price >= 0),
  unit_cost   INTEGER NOT NULL CHECK (unit_cost >= 0)
);
CREATE INDEX ix_sale_items_sale ON sale_items(sale_id);
CREATE INDEX ix_sale_items_product ON sale_items(product_id);

CREATE TABLE stock_movements (
  id          INTEGER PRIMARY KEY,
  product_id  INTEGER NOT NULL REFERENCES products(id),
  type        TEXT    NOT NULL CHECK (type IN ('initial', 'restock', 'loss', 'correction', 'sale', 'void')),
  quantity    INTEGER NOT NULL CHECK (quantity != 0),
  stock_after INTEGER NOT NULL CHECK (stock_after >= 0),
  note        TEXT    NOT NULL DEFAULT '',
  sale_id     INTEGER REFERENCES sales(id),
  created_at  TEXT    NOT NULL
);
CREATE INDEX ix_movements_product ON stock_movements(product_id, created_at);

CREATE TABLE settings (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
INSERT INTO settings(key, value) VALUES
  ('currency_code', 'COP'),
  ('currency_symbol', '$'),
  ('currency_decimals', '0');
