# common/db.py
from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from typing import Iterable, Any, Tuple, Optional
import pandas as pd
from config import DB_PATH

def connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")  # safety
    return conn

@contextmanager
def get_conn(db_path: Optional[str] = None):
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def execute(sql: str, params: Tuple[Any, ...] = (), db_path: Optional[str] = None) -> None:
    with get_conn(db_path) as c:
        c.execute(sql, params)

def executemany(sql: str, rows: Iterable[Tuple[Any, ...]], db_path: Optional[str] = None) -> None:
    with get_conn(db_path) as c:
        c.executemany(sql, rows)

def query_df(sql: str, params: Tuple[Any, ...] = (), db_path: Optional[str] = None) -> pd.DataFrame:
    with connect(db_path) as c:
        return pd.read_sql_query(sql, c, params=params)

def init_db(ddl_sql: str, db_path: Optional[str] = None) -> None:
    with get_conn(db_path) as c:
        c.executescript(ddl_sql)
