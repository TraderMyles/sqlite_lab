from __future__ import annotations
import argparse
from common.db import execute, query_df
from common.utils import parse_amount_to_cents, today_iso

def ensure_category(name: str) -> int:
    execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))
    df = query_df("SELECT category_id FROM categories WHERE name=?", (name,))
    return int(df.iloc[0]["category_id"])

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--date", default=today_iso())
    p.add_argument("--amount", required=True, help="e.g., 12.34")
    p.add_argument("--category", required=True)
    p.add_argument("--merchant", default="")
    p.add_argument("--note", default="")
    a = p.parse_args()

    cents = parse_amount_to_cents(a.amount)
    cat_id = ensure_category(a.category)

    execute("""INSERT INTO expenses(tx_date, amount_cents, category_id, merchant, note)
               VALUES (?, ?, ?, ?, ?)""",
            (a.date, cents, cat_id, a.merchant, a.note))
    print("Saved.")

if __name__ == "__main__":
    main()
