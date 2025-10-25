PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS categories (
  category_id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS expenses (
  expense_id INTEGER PRIMARY KEY,
  tx_date TEXT NOT NULL,            -- ISO date
  amount_cents INTEGER NOT NULL,    -- store in cents
  category_id INTEGER NOT NULL,
  merchant TEXT,
  note TEXT,
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(tx_date);
CREATE INDEX IF NOT EXISTS idx_expenses_cat ON expenses(category_id);
