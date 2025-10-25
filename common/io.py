from __future__ import annotations
import pandas as pd
from typing import Optional
from config import DB_PATH
import sqlite3
from pathlib import Path

def csv_to_table(csv_path: str, table_name: str, if_exists: str = "append", db_path: Optional[str] = None):
    df = pd.read_csv(csv_path)
    with sqlite3.connect(db_path or DB_PATH) as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)

def table_to_csv(table_name: str, out_path: str, db_path: Optional[str] = None):
    with sqlite3.connect(db_path or DB_PATH) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
