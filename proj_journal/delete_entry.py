from __future__ import annotations
import argparse
from common.db import get_conn, query_df
from tabulate import tabulate

def delete_entry(entry_id: int, confirm: bool):
    # Show preview before deleting
    df = query_df("SELECT entry_id, entry_date, title FROM entries WHERE entry_id=?", (entry_id,))
    if df.empty:
        print(f"No entry found with id {entry_id}")
        return
    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))

    if not confirm:
        answer = input(f"Delete entry #{entry_id}? (y/n): ").strip().lower()
        if answer != "y":
            print("Cancelled.")
            return

    with get_conn() as conn:
        conn.execute("DELETE FROM entries WHERE entry_id=?", (entry_id,))
    print(f"Deleted entry #{entry_id}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entry_id", type=int)
    ap.add_argument("--yes", action="store_true", help="Skip confirmation")
    args = ap.parse_args()
    delete_entry(args.entry_id, args.yes)

if __name__ == "__main__":
    main()
