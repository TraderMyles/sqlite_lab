from common.db import init_db, executemany
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql").read_text()

DEFAULT_CATS = [("Groceries",), ("Transport",), ("Eating Out",), ("Rent",), ("Bills",)]

def main():
    init_db(SCHEMA)
    executemany("INSERT OR IGNORE INTO categories(name) VALUES (?)", DEFAULT_CATS)
    print("Expense schema created and categories seeded.")

if __name__ == "__main__":
    main()
