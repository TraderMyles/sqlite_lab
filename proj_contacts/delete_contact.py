from __future__ import annotations
import argparse
from common.db import get_conn, query_df
from tabulate import tabulate

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", default="")
    ap.add_argument("--contact-id", type=int)
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()

    if not a.email and not a.contact_id:
        raise SystemExit("Provide --email or --contact-id")

    if a.contact_id:
        df = query_df("SELECT contact_id, full_name, email FROM contacts WHERE contact_id=?", (a.contact_id,))
    else:
        df = query_df("SELECT contact_id, full_name, email FROM contacts WHERE email=?", (a.email,))

    if df.empty:
        print("No such contact.")
        return

    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))
    if not a.yes:
        ans = input("Delete this contact and all notes? (y/n): ").strip().lower()
        if ans != "y":
            print("Cancelled.")
            return

    cid = int(df.iloc[0]["contact_id"])
    with get_conn() as conn:
        conn.execute("DELETE FROM contacts WHERE contact_id=?", (cid,))
    print(f"Deleted contact #{cid} (notes removed via cascade).")

if __name__ == "__main__":
    main()
