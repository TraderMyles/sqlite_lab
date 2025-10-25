from __future__ import annotations
import argparse, sys, textwrap
from common.db import init_db, query_df
from common.io import table_to_csv

BASIC_DDL = """
PRAGMA foreign_keys=ON;
"""

def cmd_init_db(args):
    init_db(BASIC_DDL)
    print("DB initialised.")

def cmd_sql(args):
    df = query_df(args.query)
    if df.empty:
        print("(no rows)")
    else:
        from tabulate import tabulate
        print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))

def cmd_export(args):
    table_to_csv(args.table, args.out)
    print(f"Exported {args.table} -> {args.out}")

def main():
    p = argparse.ArgumentParser(description="Project manager")
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("init-db", help="Initialise base DB")
    s1.set_defaults(func=cmd_init_db)

    s2 = sub.add_parser("sql", help="Run a SELECT and print results")
    s2.add_argument("query")
    s2.set_defaults(func=cmd_sql)

    s3 = sub.add_parser("export", help="Export a table to CSV")
    s3.add_argument("table")
    s3.add_argument("out")
    s3.set_defaults(func=cmd_export)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
